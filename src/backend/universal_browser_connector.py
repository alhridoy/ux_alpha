
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import logging
import re
import time
import hashlib

class UniversalBrowserConnector:
    """
    A connector that simplifies browser interaction for LLM agents.
    It provides:
    1. HTML simplification to make web content more consumable for LLMs
    2. Action execution to translate LLM actions into browser commands
    3. Screenshot capture for visual context
    """
    
    def __init__(self, headless: bool = False, browser_type: str = "chrome"):
        """
        Initialize the browser connector.
        
        Args:
            headless: Whether to run the browser in headless mode
            browser_type: Which browser to use ('chrome', 'firefox')
        """
        self.browser_type = browser_type
        self.driver = self._setup_driver(headless)
        self.current_page_elements = {}  # Maps element names to selectors
        self.logger = logging.getLogger(__name__)
        
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Set up and return a WebDriver instance."""
        if self.browser_type.lower() == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
        elif self.browser_type.lower() == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        return driver
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL and return simplified page content.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Simplified page representation
        """
        self.logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        # Allow time for JavaScript to load
        time.sleep(2)
        simplified_page = self.simplify_html()
        return simplified_page
    
    def simplify_html(self) -> Dict[str, Any]:
        """
        Convert the current page to a simplified representation for the LLM agent.
        
        Returns:
            Dictionary containing simplified page content:
            {
                'url': str,
                'title': str,
                'clickables': List[Dict],
                'inputs': List[Dict],
                'text_blocks': List[Dict],
                'error_message': Optional[str]
            }
        """
        self.logger.info("Simplifying HTML...")
        
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Reset element mapping
        self.current_page_elements = {}
        
        # Extract basic page info
        result = {
            'url': self.driver.current_url,
            'title': self.driver.title,
            'clickables': [],
            'inputs': [],
            'text_blocks': [],
            'error_message': None
        }
        
        # Process clickable elements (links, buttons)
        self._extract_clickables(soup, result['clickables'])
        
        # Process form input elements
        self._extract_inputs(soup, result['inputs'])
        
        # Process text blocks
        self._extract_text_blocks(soup, result['text_blocks'])
        
        return result
    
    def _generate_element_name(self, element, element_type: str) -> str:
        """Generate a hierarchical name for an element."""
        # Start with any available identifiers
        identifiers = []
        
        # Check for common attributes that help identify an element
        for attr in ['id', 'name', 'aria-label', 'title', 'placeholder', 'alt']:
            if element.get(attr):
                identifiers.append(element.get(attr).lower())
        
        # Use text content if available
        if element.text and element.text.strip():
            # Limit text length for name generation
            text = element.text.strip()
            if len(text) > 30:
                text = text[:30].rstrip() + "..."
            identifiers.append(text.lower())
        
        # If no identifiers found, use element hash
        if not identifiers:
            # Create a hash of the element's HTML
            element_html = str(element)
            element_hash = hashlib.md5(element_html.encode()).hexdigest()[:8]
            identifiers.append(f"{element_type}_{element_hash}")
        
        # Join identifiers to create name
        base_name = '_'.join([re.sub(r'[^\w]', '_', id).strip('_') for id in identifiers[:1]])
        
        # Ensure name is unique by adding a suffix if needed
        name = base_name
        counter = 1
        while name in self.current_page_elements:
            name = f"{base_name}_{counter}"
            counter += 1
        
        return name
    
    def _extract_clickables(self, soup: BeautifulSoup, clickables: List[Dict[str, Any]]) -> None:
        """Extract clickable elements from the page."""
        # Find links
        for link in soup.find_all('a', href=True):
            self._add_clickable_element(link, 'link', clickables)
        
        # Find buttons
        for button in soup.find_all(['button', 'input'], type=['button', 'submit']):
            self._add_clickable_element(button, 'button', clickables)
        
        # Find elements with click-related event handlers or roles
        click_candidates = soup.select('[onclick], [role="button"], [class*="btn"]')
        for element in click_candidates:
            if element.name not in ['a', 'button', 'input']:
                self._add_clickable_element(element, 'clickable', clickables)
    
    def _add_clickable_element(self, element, element_type: str, clickables: List[Dict[str, Any]]) -> None:
        """Add a clickable element to the clickables list."""
        # Skip hidden elements
        style = element.get('style', '')
        classes = element.get('class', [])
        
        # Skip if it appears to be hidden
        if ('display: none' in style or 
            'visibility: hidden' in style or
            'hidden' in classes or
            element.get('aria-hidden') == 'true'):
            return
        
        # Generate a name for this element
        name = self._generate_element_name(element, element_type)
        
        # Create XPath for this element
        try:
            xpath = self._generate_xpath(element)
            self.current_page_elements[name] = {'xpath': xpath, 'type': element_type}
            
            # Gather text content and description
            text = element.text.strip() if element.text else None
            description = f"{element_type.capitalize()}: {text}" if text else f"{element_type.capitalize()}"
            
            # Add to clickables
            clickables.append({
                'name': name,
                'type': element_type,
                'text': text,
                'description': description
            })
            
        except Exception as e:
            self.logger.error(f"Error processing clickable element: {e}")
    
    def _extract_inputs(self, soup: BeautifulSoup, inputs: List[Dict[str, Any]]) -> None:
        """Extract form input elements from the page."""
        for input_elem in soup.find_all(['input', 'textarea', 'select']):
            # Skip hidden or submit/button inputs
            input_type = input_elem.get('type', 'text')
            if (input_type in ['hidden', 'submit', 'button'] or
                input_elem.get('style', '').find('display: none') >= 0):
                continue
                
            # Generate a name for this element
            name = self._generate_element_name(input_elem, input_type)
            
            # Create XPath for this element
            try:
                xpath = self._generate_xpath(input_elem)
                self.current_page_elements[name] = {'xpath': xpath, 'type': 'input'}
                
                # Get label text
                label_text = None
                if input_id := input_elem.get('id'):
                    label_elem = soup.find('label', attrs={'for': input_id})
                    if label_elem:
                        label_text = label_elem.text.strip()
                
                # Get placeholder
                placeholder = input_elem.get('placeholder', '')
                
                # Create description
                description = label_text or placeholder or name
                
                # Add to inputs
                inputs.append({
                    'name': name,
                    'type': input_type,
                    'placeholder': placeholder,
                    'label': label_text,
                    'description': description,
                    'required': input_elem.get('required', False)
                })
                
            except Exception as e:
                self.logger.error(f"Error processing input element: {e}")
    
    def _extract_text_blocks(self, soup: BeautifulSoup, text_blocks: List[Dict[str, Any]]) -> None:
        """Extract meaningful text blocks from the page."""
        # Get text from headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            text = heading.text.strip()
            if text:
                text_blocks.append({
                    'type': 'heading',
                    'tag': heading.name,
                    'text': text
                })
        
        # Get paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.text.strip()
            if text and len(text) > 10:  # Skip very short text
                text_blocks.append({
                    'type': 'paragraph',
                    'tag': 'p',
                    'text': text
                })
        
        # Lists
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = list_elem.find_all('li')
            items_text = [item.text.strip() for item in items if item.text.strip()]
            if items_text:
                text_blocks.append({
                    'type': 'list',
                    'tag': list_elem.name,
                    'items': items_text
                })
    
    def _generate_xpath(self, element) -> str:
        """Generate an XPath expression that uniquely identifies an element."""
        components = []
        current = element
        
        while current and current.name != '[document]':
            # Get all siblings of the same type
            siblings = [sibling for sibling in current.parent.find_all(current.name, recursive=False)]
            
            if len(siblings) == 1:
                # If it's the only element of its type, just use the tag name
                components.insert(0, current.name)
            else:
                # If there are multiple, use the position
                position = siblings.index(current) + 1
                components.insert(0, f"{current.name}[{position}]")
            
            current = current.parent
        
        return '//' + '/'.join(components)
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action in the browser.
        
        Args:
            action: Action object with properties:
                   {'type': str, 'name': str, 'value': Optional[str], etc.}
                   
        Returns:
            Result dictionary {'success': bool, 'message': str}
        """
        action_type = action.get('type', '').lower()
        element_name = action.get('name')
        
        self.logger.info(f"Executing {action_type} action on {element_name}")
        
        try:
            if action_type == 'navigate':
                url = action.get('target', '')
                return self.navigate(url)
                
            elif action_type == 'click':
                return self._execute_click(element_name)
                
            elif action_type == 'input':
                value = action.get('value', '')
                return self._execute_input(element_name, value)
                
            elif action_type == 'scroll':
                direction = action.get('value', 'down')
                return self._execute_scroll(direction)
                
            elif action_type == 'back':
                self.driver.back()
                time.sleep(1)
                return {'success': True, 'message': 'Navigated back'}
                
            elif action_type == 'wait':
                seconds = int(action.get('value', 2))
                time.sleep(seconds)
                return {'success': True, 'message': f'Waited for {seconds} seconds'}
                
            else:
                return {'success': False, 'message': f'Unknown action type: {action_type}'}
        
        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}")
            return {'success': False, 'message': f'Action failed: {str(e)}'}
    
    def _execute_click(self, element_name: str) -> Dict[str, bool]:
        """Execute a click action."""
        if element_name not in self.current_page_elements:
            return {'success': False, 'message': f'Element "{element_name}" not found'}
        
        element_info = self.current_page_elements[element_name]
        try:
            # Wait for the element to be clickable
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, element_info['xpath']))
            )
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            # Highlight element temporarily
            self._highlight_element(element)
            
            # Click the element
            element.click()
            time.sleep(1)  # Wait for any page changes
            
            # Return simplified page after click
            simplified_page = self.simplify_html()
            simplified_page['success'] = True
            simplified_page['message'] = f'Clicked on {element_name}'
            return simplified_page
            
        except TimeoutException:
            return {'success': False, 'message': f'Element "{element_name}" not found or not clickable'}
        except Exception as e:
            return {'success': False, 'message': f'Click failed: {str(e)}'}
    
    def _execute_input(self, element_name: str, value: str) -> Dict[str, bool]:
        """Execute an input action."""
        if element_name not in self.current_page_elements:
            return {'success': False, 'message': f'Element "{element_name}" not found'}
        
        element_info = self.current_page_elements[element_name]
        try:
            # Wait for the element to be present
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, element_info['xpath']))
            )
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            # Highlight element temporarily
            self._highlight_element(element)
            
            # Clear existing value and input new value
            element.clear()
            element.send_keys(value)
            time.sleep(0.5)  # Small wait after input
            
            return {'success': True, 'message': f'Entered "{value}" into {element_name}'}
            
        except TimeoutException:
            return {'success': False, 'message': f'Element "{element_name}" not found'}
        except Exception as e:
            return {'success': False, 'message': f'Input failed: {str(e)}'}
    
    def _execute_scroll(self, direction: str = 'down') -> Dict[str, bool]:
        """Execute a scroll action."""
        try:
            if direction.lower() == 'down':
                self.driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
            elif direction.lower() == 'up':
                self.driver.execute_script("window.scrollBy(0, -window.innerHeight / 2);")
            elif direction.lower() == 'top':
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction.lower() == 'bottom':
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(0.5)
            return {'success': True, 'message': f'Scrolled {direction}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Scroll failed: {str(e)}'}
    
    def _highlight_element(self, element, duration: float = 0.5) -> None:
        """Highlight an element temporarily."""
        original_style = element.get_attribute("style")
        self.driver.execute_script("""
            var element = arguments[0];
            var originalStyle = element.getAttribute('style') || '';
            element.setAttribute('style', originalStyle + '; border: 2px solid red; background-color: yellow; transition: all 0.3s;');
        """, element)
        
        time.sleep(duration)
        
        self.driver.execute_script("""
            var element = arguments[0];
            var originalStyle = arguments[1];
            element.setAttribute('style', originalStyle);
        """, element, original_style)
    
    def take_screenshot(self, filepath: Optional[str] = None) -> str:
        """
        Take a screenshot of the current browser window.
        
        Args:
            filepath: Optional path to save the screenshot
            
        Returns:
            Path to the saved screenshot file
        """
        if filepath is None:
            filepath = f"screenshot_{int(time.time())}.png"
            
        self.driver.save_screenshot(filepath)
        return filepath
    
    def close(self) -> None:
        """Close the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None
