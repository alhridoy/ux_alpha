
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import logging
import re
import time
import hashlib

# Stagehand integration
try:
    from browserbasehq import stagehand
    STAGEHAND_AVAILABLE = True
except ImportError:
    STAGEHAND_AVAILABLE = False

class UniversalBrowserConnector:
    """
    A connector that simplifies browser interaction for LLM agents using Stagehand.
    It provides:
    1. HTML simplification to make web content more consumable for LLMs
    2. Action execution to translate LLM actions into browser commands
    3. Data extraction for gathering structured information
    """
    
    def __init__(self, headless: bool = False, stagehand_api_key: Optional[str] = None):
        """
        Initialize the browser connector.
        
        Args:
            headless: Whether to run the browser in headless mode
            stagehand_api_key: API key for Stagehand (required)
        """
        self.stagehand_api_key = stagehand_api_key
        self.stagehand_page = None
        self.stagehand = None
        
        if not STAGEHAND_AVAILABLE:
            raise ImportError("Stagehand is required but not available. Please install with 'pip install browserbasehq-stagehand'")
        
        if not stagehand_api_key:
            raise ValueError("Stagehand API key is required")
        
        self._setup_stagehand(headless)
            
        self.current_page_elements = {}  # Maps element names to selectors
        self.logger = logging.getLogger(__name__)
        
    def _setup_stagehand(self, headless: bool):
        """Set up Stagehand for browser automation."""
        try:
            self.stagehand = stagehand.Stagehand({
                "env": "LOCAL",
                "modelName": "gpt-4o",
                "modelClientOptions": {
                    "apiKey": self.stagehand_api_key,
                },
                "headless": headless
            })
            self.stagehand.init()
            self.stagehand_page = self.stagehand.page
            self.logger.info("Stagehand initialized successfully")
        except Exception as e:
            self.logger.error(f"Error setting up Stagehand: {str(e)}")
            raise
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL and return simplified page content.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Simplified page representation
        """
        self.logger.info(f"Navigating to: {url}")
        
        try:
            self.stagehand_page.goto(url)
            # Allow time for JavaScript to load
            time.sleep(2)
            
            # Get page content and simplify
            simplified_page = self.simplify_html()
            return simplified_page
        except Exception as e:
            self.logger.error(f"Error navigating with Stagehand: {str(e)}")
            return {
                'url': url,
                'title': '',
                'clickables': [],
                'inputs': [],
                'text_blocks': [],
                'error_message': str(e)
            }
    
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
        
        try:
            # Get page content
            page_content = self.stagehand_page.content()
            url = self.stagehand_page.url()
            
            # Parse the HTML
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Reset element mapping
            self.current_page_elements = {}
            
            # Extract basic page info
            result = {
                'url': url,
                'title': soup.title.text if soup.title else "",
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
        except Exception as e:
            self.logger.error(f"Error simplifying HTML: {str(e)}")
            return {
                'url': self.stagehand_page.url() if self.stagehand_page else "",
                'title': "",
                'clickables': [],
                'inputs': [],
                'text_blocks': [],
                'error_message': str(e)
            }
    
    def _extract_clickables(self, soup, clickables_list):
        """Extract clickable elements from the soup and add to the list."""
        # Extract links
        for link in soup.find_all('a'):
            self._add_clickable_element(link, 'link', clickables_list)
        
        # Extract buttons
        for button in soup.find_all(['button', 'input']):
            if button.name == 'input' and button.get('type', '').lower() not in ['submit', 'button', 'reset']:
                continue
            self._add_clickable_element(button, 'button', clickables_list)
        
        # Extract other clickable elements with roles
        for elem in soup.find_all(attrs={'role': ['button', 'link', 'tab', 'menuitem']}):
            self._add_clickable_element(elem, elem.get('role'), clickables_list)
    
    def _add_clickable_element(self, element, elem_type, clickables_list):
        """Add a clickable element to the list with appropriate properties."""
        # Skip if no text and no useful attributes
        text = element.get_text().strip()
        if not text and not element.get('aria-label') and not element.get('title'):
            return
        
        # Generate a unique name for this element
        name = self._generate_element_name(element, text, elem_type)
        
        # Skip duplicates
        if name in self.current_page_elements:
            return
        
        # Create description
        description = f"{elem_type.capitalize()}: {text}"
        if not text:
            aria_label = element.get('aria-label', '')
            title = element.get('title', '')
            description = f"{elem_type.capitalize()}: {aria_label or title}"
        
        # Store element for later retrieval
        self.current_page_elements[name] = element
        
        # Add to clickables list
        clickables_list.append({
            'name': name,
            'type': elem_type,
            'text': text,
            'description': description
        })
    
    def _extract_inputs(self, soup, inputs_list):
        """Extract input elements from the soup and add to the list."""
        # Process form input elements
        for input_elem in soup.find_all(['input', 'textarea', 'select']):
            input_type = input_elem.get('type', 'text').lower()
            
            # Skip submit, button, hidden types
            if input_type in ['submit', 'button', 'reset', 'hidden']:
                continue
            
            # Get label
            label_text = ""
            id_attr = input_elem.get('id')
            if id_attr:
                label = soup.find('label', attrs={'for': id_attr})
                if label:
                    label_text = label.get_text().strip()
            
            # If no label found, try placeholder or name
            if not label_text:
                label_text = input_elem.get('placeholder', input_elem.get('name', input_elem.get('aria-label', '')))
            
            # Generate name for this element
            elem_name = self._generate_element_name(input_elem, label_text, input_type)
            
            # Description
            description = f"{input_type.capitalize()} field"
            if label_text:
                description += f" labeled '{label_text}'"
            
            # Store element for later retrieval
            self.current_page_elements[elem_name] = input_elem
            
            # Add to inputs list
            inputs_list.append({
                'name': elem_name,
                'type': input_type,
                'label': label_text,
                'description': description
            })
    
    def _extract_text_blocks(self, soup, text_blocks_list):
        """Extract meaningful text blocks from the soup and add to the list."""
        # Extract headings
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(heading_tag):
                text = heading.get_text().strip()
                if text:
                    text_blocks_list.append({
                        'type': 'heading',
                        'tag': heading_tag,
                        'text': text
                    })
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                text_blocks_list.append({
                    'type': 'paragraph',
                    'text': text
                })
        
        # Extract lists
        for list_tag in ['ul', 'ol']:
            for list_elem in soup.find_all(list_tag):
                items = [li.get_text().strip() for li in list_elem.find_all('li')]
                items = [item for item in items if item]  # Filter out empty items
                if items:
                    text_blocks_list.append({
                        'type': 'list',
                        'list_type': 'unordered' if list_tag == 'ul' else 'ordered',
                        'items': items
                    })
    
    def _generate_element_name(self, element, text_content, elem_type):
        """Generate a unique name for the element based on its attributes."""
        # Try to use id, name, or aria-label
        element_id = element.get('id', '')
        element_name = element.get('name', '')
        aria_label = element.get('aria-label', '')
        
        # If element has a clear identifier, use it
        if element_id:
            return f"{elem_type}_{element_id.replace(' ', '_').lower()}"
        if element_name:
            return f"{elem_type}_{element_name.replace(' ', '_').lower()}"
            
        # Otherwise use the text content
        if text_content:
            # Limit length and replace spaces
            text = text_content[:20].strip().replace(' ', '_').lower()
            # Keep only alphanumeric and underscore
            text = ''.join(c for c in text if c.isalnum() or c == '_')
            if text:
                return f"{elem_type}_{text}"
        
        # Last resort - use aria-label or a hash
        if aria_label:
            aria_text = aria_label[:20].strip().replace(' ', '_').lower()
            return f"{elem_type}_{aria_text}"
        else:
            # Create a unique hash if nothing else works
            elem_html = str(element)
            elem_hash = hashlib.md5(elem_html.encode()).hexdigest()[:8]
            return f"{elem_type}_{elem_hash}"
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action in the browser using Stagehand.
        
        Args:
            action: Action object with properties:
                   {'type': str, 'name': str, 'value': Optional[str], etc.}
                   
        Returns:
            Result dictionary {'success': bool, 'message': str}
        """
        action_type = action.get('type', '').lower()
        
        self.logger.info(f"Executing {action_type} action")
        
        try:
            if action_type == 'navigate':
                url = action.get('target', '')
                return self.navigate(url)
                
            # For most actions, use Stagehand's observe + act pattern
            elif action_type in ['click', 'input', 'scroll', 'submit']:
                # Get reasoning or description from the action
                description = action.get('reasoning', '') or action.get('description', '')
                
                if not description:
                    # Construct a description based on action type and target
                    if action_type == 'click':
                        description = f"Click on {action.get('name', 'the element')}"
                    elif action_type == 'input':
                        description = f"Type '{action.get('value', '')}' into {action.get('name', 'the input field')}"
                    elif action_type == 'scroll':
                        direction = action.get('value', 'down')
                        description = f"Scroll {direction}"
                    elif action_type == 'submit':
                        description = f"Submit the form"
                
                # Use Stagehand's observe + act pattern
                stagehand_actions = self.stagehand_page.observe(description)
                
                if not stagehand_actions:
                    return {'success': False, 'message': f'Stagehand could not determine how to {action_type} {action.get("name", "")}'}
                
                # Take the first action (most likely)
                stagehand_action = stagehand_actions[0]
                
                # Execute the action
                self.stagehand_page.act(stagehand_action)
                
                # Wait a moment for the action to take effect
                time.sleep(1)
                
                # Return simplified page after action
                simplified_page = self.simplify_html()
                simplified_page['success'] = True
                simplified_page['message'] = f'Executed {action_type} action: {description}'
                return simplified_page
                
            elif action_type == 'back':
                self.stagehand_page.goBack()
                time.sleep(1)
                simplified_page = self.simplify_html()
                simplified_page['success'] = True
                simplified_page['message'] = 'Navigated back'
                return simplified_page
                
            elif action_type == 'wait':
                seconds = int(action.get('value', 2))
                time.sleep(seconds)
                return {'success': True, 'message': f'Waited for {seconds} seconds'}
                
            else:
                return {'success': False, 'message': f'Unsupported action type: {action_type}'}
                
        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}")
            return {'success': False, 'message': f'Action failed: {str(e)}'}
    
    def extract_data(self, instruction: str, schema_definition: Any) -> Dict[str, Any]:
        """
        Extract structured data from the current page using Stagehand.
        
        Args:
            instruction: What data to extract
            schema_definition: JSON schema definition
            
        Returns:
            Extracted data
        """
        try:
            extracted_data = self.stagehand_page.extract({
                'instruction': instruction,
                'schema': schema_definition
            })
            
            return {
                'success': True,
                'data': extracted_data
            }
        except Exception as e:
            self.logger.error(f"Error extracting data with Stagehand: {str(e)}")
            return {'success': False, 'message': f'Data extraction failed: {str(e)}'}
    
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
        
        self.stagehand_page.screenshot(path=filepath)
        return filepath
    
    def close(self) -> None:
        """Close the browser session."""
        if hasattr(self, 'stagehand'):
            try:
                self.stagehand.close()
            except Exception as e:
                self.logger.error(f"Error closing Stagehand: {str(e)}")
