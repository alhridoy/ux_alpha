
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

# Stagehand integration (conditionally imported)
try:
    from browserbasehq import stagehand
    STAGEHAND_AVAILABLE = True
except ImportError:
    STAGEHAND_AVAILABLE = False

class UniversalBrowserConnector:
    """
    A connector that simplifies browser interaction for LLM agents.
    It provides:
    1. HTML simplification to make web content more consumable for LLMs
    2. Action execution to translate LLM actions into browser commands
    3. Screenshot capture for visual context
    
    Supports both Selenium and Stagehand for browser automation.
    """
    
    def __init__(self, headless: bool = False, browser_type: str = "chrome", use_stagehand: bool = False, stagehand_api_key: Optional[str] = None):
        """
        Initialize the browser connector.
        
        Args:
            headless: Whether to run the browser in headless mode
            browser_type: Which browser to use ('chrome', 'firefox')
            use_stagehand: Whether to use Stagehand for browser automation
            stagehand_api_key: API key for Stagehand (required if use_stagehand is True)
        """
        self.browser_type = browser_type
        self.use_stagehand = use_stagehand and STAGEHAND_AVAILABLE
        self.stagehand_api_key = stagehand_api_key
        self.stagehand_page = None
        
        if self.use_stagehand:
            if not stagehand_api_key:
                raise ValueError("Stagehand API key is required when use_stagehand is True")
            self._setup_stagehand()
        else:
            self.driver = self._setup_driver(headless)
            
        self.current_page_elements = {}  # Maps element names to selectors
        self.logger = logging.getLogger(__name__)
        
    def _setup_stagehand(self):
        """Set up Stagehand for browser automation."""
        try:
            self.stagehand = stagehand.Stagehand({
                "env": "LOCAL",
                "modelName": "gpt-4o",
                "modelClientOptions": {
                    "apiKey": self.stagehand_api_key,
                }
            })
            self.stagehand.init()
            self.stagehand_page = self.stagehand.page
            self.logger.info("Stagehand initialized successfully")
        except Exception as e:
            self.logger.error(f"Error setting up Stagehand: {str(e)}")
            self.use_stagehand = False
            self.driver = self._setup_driver(headless=False)
        
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
        
        if self.use_stagehand and self.stagehand_page:
            try:
                self.stagehand_page.goto(url)
                # Allow time for JavaScript to load
                time.sleep(2)
                
                # Get page content and simplify
                page_content = self.stagehand_page.content()
                simplified_page = self._simplify_stagehand_html(page_content, url)
                simplified_page['url'] = url
                
                return simplified_page
            except Exception as e:
                self.logger.error(f"Error navigating with Stagehand: {str(e)}")
                # Fall back to Selenium
                self.logger.info("Falling back to Selenium")
                self.use_stagehand = False
                self.driver = self._setup_driver(headless=False)
        
        # Using Selenium
        self.driver.get(url)
        # Allow time for JavaScript to load
        time.sleep(2)
        simplified_page = self.simplify_html()
        return simplified_page
    
    def _simplify_stagehand_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Simplify HTML content from Stagehand.
        
        Args:
            html_content: HTML content from Stagehand
            url: Current URL
            
        Returns:
            Simplified page representation
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
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
        
        if self.use_stagehand and self.stagehand_page:
            try:
                page_content = self.stagehand_page.content()
                url = self.stagehand_page.url()
                return self._simplify_stagehand_html(page_content, url)
            except Exception as e:
                self.logger.error(f"Error simplifying HTML with Stagehand: {str(e)}")
        
        # Using Selenium
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
    
    # ... keep existing code (generate_element_name, extract_clickables, add_clickable_element, extract_inputs, extract_text_blocks, generate_xpath)
    
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
            # Use Stagehand if available
            if self.use_stagehand and self.stagehand_page:
                return self._execute_stagehand_action(action)
            
            # Fall back to Selenium
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
    
    def _execute_stagehand_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action using Stagehand.
        
        Args:
            action: Action object
            
        Returns:
            Result dictionary
        """
        action_type = action.get('type', '').lower()
        
        try:
            if action_type == 'navigate':
                url = action.get('target', '')
                self.stagehand_page.goto(url)
                return {'success': True, 'message': f'Navigated to {url}'}
                
            elif action_type in ['click', 'input']:
                # Get reasoning or description from the action
                description = action.get('reasoning', '') or action.get('description', '')
                
                if not description:
                    # Construct a description based on action type and target
                    if action_type == 'click':
                        description = f"Click on {action.get('name', 'the element')}"
                    elif action_type == 'input':
                        description = f"Type '{action.get('value', '')}' into {action.get('name', 'the input field')}"
                
                # Use Stagehand's observe + act pattern
                stagehand_actions = self.stagehand_page.observe(description)
                
                if not stagehand_actions:
                    return {'success': False, 'message': f'Stagehand could not determine how to {action_type} {action.get("name")}'}
                
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
                
            elif action_type == 'scroll':
                direction = action.get('value', 'down')
                if direction.lower() == 'down':
                    self.stagehand_page.evaluate("window.scrollBy(0, window.innerHeight / 2);")
                elif direction.lower() == 'up':
                    self.stagehand_page.evaluate("window.scrollBy(0, -window.innerHeight / 2);")
                elif direction.lower() == 'top':
                    self.stagehand_page.evaluate("window.scrollTo(0, 0);")
                elif direction.lower() == 'bottom':
                    self.stagehand_page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                
                return {'success': True, 'message': f'Scrolled {direction}'}
                
            elif action_type == 'back':
                self.stagehand_page.goBack()
                return {'success': True, 'message': 'Navigated back'}
                
            elif action_type == 'wait':
                seconds = int(action.get('value', 2))
                time.sleep(seconds)
                return {'success': True, 'message': f'Waited for {seconds} seconds'}
                
            else:
                return {'success': False, 'message': f'Unsupported action type for Stagehand: {action_type}'}
                
        except Exception as e:
            self.logger.error(f"Error executing Stagehand action: {str(e)}")
            return {'success': False, 'message': f'Stagehand action failed: {str(e)}'}
    
    def extract_data(self, instruction: str, schema_definition: Any) -> Dict[str, Any]:
        """
        Extract structured data from the current page using Stagehand.
        
        Args:
            instruction: What data to extract
            schema_definition: JSON schema definition
            
        Returns:
            Extracted data
        """
        if not self.use_stagehand or not self.stagehand_page:
            return {'success': False, 'message': 'Stagehand is not available for data extraction'}
        
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
    
    def _execute_click(self, element_name: str) -> Dict[str, bool]:
        """Execute a click action."""
        # ... keep existing code (execute_click implementation)
        
    def _execute_input(self, element_name: str, value: str) -> Dict[str, bool]:
        """Execute an input action."""
        # ... keep existing code (execute_input implementation)
    
    def _execute_scroll(self, direction: str = 'down') -> Dict[str, bool]:
        """Execute a scroll action."""
        # ... keep existing code (execute_scroll implementation)
    
    def _highlight_element(self, element, duration: float = 0.5) -> None:
        """Highlight an element temporarily."""
        # ... keep existing code (highlight_element implementation)
    
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
        
        if self.use_stagehand and self.stagehand_page:
            self.stagehand_page.screenshot(path=filepath)
        else:
            self.driver.save_screenshot(filepath)
            
        return filepath
    
    def close(self) -> None:
        """Close the browser session."""
        if self.use_stagehand and hasattr(self, 'stagehand'):
            try:
                self.stagehand.close()
            except Exception as e:
                self.logger.error(f"Error closing Stagehand: {str(e)}")
                
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.driver = None
