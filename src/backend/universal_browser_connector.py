
"""
Universal Browser Connector using Stagehand.
This module provides a connector that simplifies browser interaction for LLM agents.
"""

import os
import json
import logging
import re
import time
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

    def __init__(self,
                headless: bool = None,
                use_browserbase: bool = None,
                stagehand_api_key: Optional[str] = None,
                browserbase_api_key: Optional[str] = None,
                browserbase_project_id: Optional[str] = None,
                model_name: str = None):
        """
        Initialize the browser connector.

        Args:
            headless: Whether to run the browser in headless mode
            use_browserbase: Whether to use Browserbase cloud or local browser
            stagehand_api_key: API key for Stagehand (required if not using env vars)
            browserbase_api_key: API key for Browserbase (required if use_browserbase=True)
            browserbase_project_id: Project ID for Browserbase (required if use_browserbase=True)
            model_name: LLM model to use (e.g., "gpt-4o", "claude-3-5-sonnet-latest")
        """
        # Get settings from environment if not provided
        self.headless = headless if headless is not None else os.getenv("HEADLESS", "false").lower() == "true"
        self.use_browserbase = use_browserbase if use_browserbase is not None else os.getenv("USE_BROWSERBASE", "false").lower() == "true"
        self.model_name = model_name or os.getenv("DEFAULT_MODEL", "gpt-4o")

        # Get API keys from environment if not provided
        self.stagehand_api_key = stagehand_api_key or os.getenv("OPENAI_API_KEY")
        self.browserbase_api_key = browserbase_api_key or os.getenv("BROWSERBASE_API_KEY")
        self.browserbase_project_id = browserbase_project_id or os.getenv("BROWSERBASE_PROJECT_ID")

        # Initialize other attributes
        self.stagehand = None
        self.stagehand_page = None
        self.action_cache = {}  # Cache for actions
        self.current_page_elements = {}  # Maps element names to selectors
        self.logger = logging.getLogger(__name__)

        # Check requirements
        if not STAGEHAND_AVAILABLE:
            raise ImportError("Stagehand is required but not available. Please install with 'pip install browserbasehq-stagehand'")

        if not self.stagehand_api_key:
            raise ValueError("Stagehand API key is required. Set OPENAI_API_KEY environment variable or pass stagehand_api_key parameter.")

        if self.use_browserbase and (not self.browserbase_api_key or not self.browserbase_project_id):
            raise ValueError("Browserbase API key and Project ID are required when use_browserbase=True. Set BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables or pass parameters.")

        # Set up Stagehand
        self._setup_stagehand()

    def _setup_stagehand(self):
        """Set up Stagehand for browser automation."""
        try:
            # Configure Stagehand based on whether we're using Browserbase or local browser
            if self.use_browserbase:
                self.logger.info("Setting up Stagehand with Browserbase")
                self.stagehand = stagehand.Stagehand({
                    "env": "BROWSERBASE",
                    "apiKey": self.browserbase_api_key,
                    "projectId": self.browserbase_project_id,
                    "modelName": self.model_name,
                    "modelClientOptions": {
                        "apiKey": self.stagehand_api_key,
                    },
                    "headless": self.headless
                })
            else:
                self.logger.info("Setting up Stagehand locally")
                self.stagehand = stagehand.Stagehand({
                    "env": "LOCAL",
                    "modelName": self.model_name,
                    "modelClientOptions": {
                        "apiKey": self.stagehand_api_key,
                    },
                    "headless": self.headless
                })

            # Initialize Stagehand
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

    def observe(self, instruction: str = "Find actions that can be performed on this page") -> List[Dict[str, Any]]:
        """
        Observe the page to find potential actions.

        Args:
            instruction: Natural language instruction for observation

        Returns:
            List of potential actions with selectors and descriptions
        """
        self.logger.info(f"Observing page with instruction: {instruction}")
        try:
            observations = self.stagehand_page.observe(instruction)
            return observations
        except Exception as e:
            self.logger.error(f"Error observing page: {str(e)}")
            return []

    def act(self, action_or_description: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute an action on the page.

        Args:
            action_or_description: Either a string description or an action object

        Returns:
            Result dictionary with simplified page state
        """
        if isinstance(action_or_description, str):
            self.logger.info(f"Acting on page with description: {action_or_description}")
        else:
            self.logger.info(f"Acting on page with action: {action_or_description.get('description', 'Unknown action')}")

        try:
            result = self.stagehand_page.act(action_or_description)
            # Allow time for action to take effect
            time.sleep(1)

            # Get updated page state
            simplified_page = self.simplify_html()
            simplified_page['success'] = True
            simplified_page['message'] = f'Executed action successfully'
            return simplified_page
        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}")
            return {'success': False, 'message': f'Action failed: {str(e)}'}

    def act_with_cache(self, action_description: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an action with caching to avoid redundant LLM calls.

        Args:
            action_description: Natural language description of the action
            cache_key: Optional key for caching (defaults to hash of description)

        Returns:
            Result dictionary with simplified page state
        """
        if not cache_key:
            cache_key = hashlib.md5(action_description.encode()).hexdigest()

        if cache_key in self.action_cache:
            self.logger.info(f"Using cached action for: {action_description}")
            cached_action = self.action_cache[cache_key]
            return self.act(cached_action)

        observations = self.observe(action_description)
        if observations:
            self.action_cache[cache_key] = observations[0]
            return self.act(observations[0])

        return {'success': False, 'message': 'No actions found'}

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

                # Use act method which internally uses Stagehand's observe + act pattern
                return self.act(description)

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
            schema_definition: JSON schema definition or Zod schema

        Returns:
            Extracted data
        """
        self.logger.info(f"Extracting data with instruction: {instruction}")
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

    def setup_agent(self, provider: str = "openai", model: Optional[str] = None) -> Any:
        """
        Set up a computer use agent for more complex tasks.

        Args:
            provider: LLM provider ("openai" or "anthropic")
            model: Model name (defaults to the one set during initialization)

        Returns:
            Stagehand agent object
        """
        agent_config = {
            'provider': provider,
            'model': model or self.model_name,
        }

        self.logger.info(f"Setting up agent with config: {agent_config}")
        return self.stagehand.agent(agent_config)

    def execute_complex_task(self, task_description: str, provider: str = "openai", model: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a complex task using a computer use agent.

        Args:
            task_description: Natural language description of the task
            provider: LLM provider ("openai" or "anthropic")
            model: Model name (defaults to the one set during initialization)

        Returns:
            Result dictionary with task execution results
        """
        self.logger.info(f"Executing complex task: {task_description}")
        agent = self.setup_agent(provider, model)
        try:
            result = agent.execute(task_description)
            return {
                'success': True,
                'message': result.get('message', ''),
                'actions': result.get('actions', [])
            }
        except Exception as e:
            self.logger.error(f"Error executing complex task: {str(e)}")
            return {'success': False, 'message': f'Task execution failed: {str(e)}'}

    def take_screenshot(self, filepath: Optional[str] = None) -> str:
        """
        Take a screenshot of the current browser window.

        Args:
            filepath: Optional path to save the screenshot

        Returns:
            Base64-encoded screenshot data or path to the saved screenshot file
        """
        try:
            # If no filepath is provided, return base64-encoded screenshot
            if filepath is None:
                # Take screenshot as bytes
                screenshot_bytes = self.stagehand_page.screenshot()
                # Convert to base64
                import base64
                base64_screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
                # Return as data URL
                return f"data:image/png;base64,{base64_screenshot}"
            else:
                # Save to file if filepath is provided
                self.stagehand_page.screenshot(path=filepath)
                return filepath
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return ""

    def close(self) -> None:
        """Close the browser session."""
        if hasattr(self, 'stagehand'):
            try:
                self.stagehand.close()
            except Exception as e:
                self.logger.error(f"Error closing Stagehand: {str(e)}")
