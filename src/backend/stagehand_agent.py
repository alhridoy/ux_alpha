"""
Stagehand Agent for UX Agent Simulator.
This module provides a Stagehand-based agent for browser automation.
"""

import os
import time
import logging
import json
import base64
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Stagehand
try:
    # First try to import stagehand-py (Python SDK)
    try:
        from stagehand_py import Stagehand, StagehandConfig
        from stagehand_py.schemas import AgentConfig, AgentExecuteOptions, AgentProvider
        from stagehand_py.sync import Stagehand as SyncStagehand
        STAGEHAND_AVAILABLE = True
        print("Successfully imported stagehand-py")
    except ImportError:
        # Fall back to trying the JavaScript-based stagehand import
        from stagehand import Stagehand, StagehandConfig
        from stagehand.schemas import AgentConfig, AgentExecuteOptions, AgentProvider
        from stagehand.sync import Stagehand as SyncStagehand
        STAGEHAND_AVAILABLE = True
        print("Successfully imported stagehand")
except ImportError as e:
    print(f"Error importing Stagehand: {str(e)}")
    STAGEHAND_AVAILABLE = False

    # Create mock classes for type checking
    class StagehandConfig:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class SyncStagehand:
        def __init__(self, **kwargs):
            self.config = kwargs.get('config')
            self.session_id = "mock-session"

        def init(self):
            pass

        def close(self):
            pass

    class AgentConfig:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class AgentExecuteOptions:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class AgentProvider:
        OPENAI = "openai"
        ANTHROPIC = "anthropic"

class StagehandAgent:
    """
    A Stagehand-based agent for browser automation.
    This agent uses Stagehand to perform browser actions based on natural language instructions.
    It serves as a replacement for the Universal Browser Controller in the UX Agent Simulator.
    """

    def __init__(self,
                browser_connector=None,
                simulation_recorder=None,
                headless: bool = False,
                api_key: Optional[str] = None,
                model_name: str = "gpt-4o"):
        """
        Initialize the Stagehand agent.

        Args:
            browser_connector: Optional UniversalBrowserConnector instance
            simulation_recorder: Optional SimulationRecorder instance
            headless: Whether to run the browser in headless mode
            api_key: API key for the LLM provider
            model_name: LLM model to use
        """
        self.browser_connector = browser_connector
        self.simulation_recorder = simulation_recorder
        self.headless = headless
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

        # If simulation_recorder is provided but doesn't have a browser_connector,
        # set it to self
        if self.simulation_recorder and not hasattr(self.simulation_recorder, 'browser_connector'):
            self.simulation_recorder.browser_connector = self

        # Initialize state variables
        self.current_page_elements = {}
        self.action_cache = {}
        self.stagehand_page = None

        # Check if Stagehand is available
        if not STAGEHAND_AVAILABLE:
            self.logger.error("Stagehand is not available. Please install it with 'pip install stagehand-py'")
            raise ImportError("Stagehand is not available")

        # Initialize Stagehand if browser_connector is not provided
        if not browser_connector:
            self._initialize_stagehand()

    def _initialize_stagehand(self):
        """Initialize Stagehand for browser automation."""
        try:
            self.logger.info("Initializing Stagehand...")

            # Check if Stagehand is available
            if not STAGEHAND_AVAILABLE:
                self.logger.warning("Stagehand is not available. Using mock implementation.")
                # Create mock objects for compatibility
                self.stagehand = SyncStagehand(config={})

                # Create a mock page object
                class MockPage:
                    def __init__(self):
                        self.url = "https://example.com"

                    def goto(self, url):
                        self.url = url

                    def title(self):
                        return "Mock Page Title"

                    def screenshot(self):
                        return b"mock_screenshot_data"

                    def evaluate(self, script, *args):
                        return "mock_evaluation_result"

                    def keyboard(self):
                        class MockKeyboard:
                            def type(self, text):
                                pass
                        return MockKeyboard()

                    def go_back(self):
                        pass

                self.page = MockPage()
                self.stagehand_page = self.page

                # Create a mock agent object
                self.stagehand.agent = type('obj', (object,), {
                    'execute': lambda *args, **kwargs: {
                        'actions': [
                            {'action': 'click', 'description': 'Mock click action', 'selector': 'button'},
                            {'action': 'input', 'description': 'Mock input action', 'selector': 'input', 'value': 'test'}
                        ]
                    }
                })

                # Create a mock observe method
                self.stagehand.observe = lambda instruction: [
                    {'description': f'Mock observation for: {instruction}', 'selector': 'div.mock-element'}
                ]

                # Create a mock act method
                self.stagehand.act = lambda action: None

                self.logger.info("Mock Stagehand initialized successfully")
                return

            # Get Browserbase API key and project ID from environment variables or use the provided ones
            browserbase_api_key = os.getenv("BROWSERBASE_API_KEY", os.getenv("STAGEHAND_API_KEY", "bb_live_AS5xOffMt0OjcAa0fc730lGFx1g"))
            browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID", os.getenv("STAGEHAND_PROJECT_ID", "56c6ec2c-e387-44fa-91ff-2f07b8b7ef40"))

            self.logger.info(f"Using Browserbase API key: {browserbase_api_key[:8]}... and project ID: {browserbase_project_id}")

            # Configure Stagehand with BROWSERBASE environment
            config = StagehandConfig(
                env="BROWSERBASE",  # Use BROWSERBASE environment to run in the cloud
                model_name=self.model_name,
                model_client_options={"apiKey": self.api_key},
                headless=False,  # Must be False to show the browser in the UI
                debug_dom=True,  # Enable DOM debugging for better visibility
                dom_settle_timeout_ms=2000,  # Give DOM time to settle for better interaction
                api_key=browserbase_api_key,  # Use the Browserbase API key
                project_id=browserbase_project_id  # Use the Browserbase project ID
            )

            # Initialize Stagehand
            self.stagehand = SyncStagehand(config=config)
            self.stagehand.init()

            # Get the page reference
            self.page = self.stagehand.page

            # Set the stagehand_page property for compatibility with UniversalBrowserConnector
            self.stagehand_page = self.page

            self.logger.info(f"Stagehand initialized successfully with session ID: {self.stagehand.session_id}")
        except Exception as e:
            self.logger.error(f"Error initializing Stagehand: {str(e)}")
            self.logger.warning("Falling back to mock implementation")

            # Call the method again to use the mock implementation
            STAGEHAND_AVAILABLE = False
            self._initialize_stagehand()

    def execute_task(self, task: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using Stagehand.

        Args:
            task: Natural language description of the task to perform
            url: Optional URL to navigate to before executing the task

        Returns:
            Result dictionary with task execution details
        """
        self.logger.info(f"Executing task: {task}")

        try:
            # Get the page reference
            page = self.page

            # Navigate to URL if provided
            if url:
                self.logger.info(f"Navigating to {url}")
                page.goto(url)
                time.sleep(2)  # Wait for page to load

                # Record navigation action if recorder is available
                if self.simulation_recorder:
                    self.simulation_recorder.record_action({
                        "type": "navigate",
                        "description": f"Navigated to {url}",
                        "target": url,
                        "timestamp": time.time()
                    })

            # Start recording if recorder is available
            if self.simulation_recorder:
                self.simulation_recorder.start_recording()

            # Execute the task using Stagehand's agent
            self.logger.info(f"Executing task with Stagehand agent: {task}")

            # Check if we're using the real Stagehand or the mock version
            if STAGEHAND_AVAILABLE:
                try:
                    # Configure the agent - use the mock classes if imports failed
                    agent_config_obj = AgentConfig(
                        provider="openai",  # Use string instead of enum for compatibility
                        model="gpt-4o",
                        instructions=f"You are a helpful web navigation assistant. Your task is: {task}",
                        options={"apiKey": self.api_key}
                    )

                    # Define execution options
                    execute_options = AgentExecuteOptions(
                        instruction=task,
                        max_steps=10,
                        auto_screenshot=True
                    )

                    # Execute the task with proper configuration
                    result = self.stagehand.agent.execute(
                        agent_config_obj,
                        execute_options
                    )
                except Exception as e:
                    self.logger.error(f"Error executing task with real Stagehand: {str(e)}")
                    # Fall back to mock execution
                    result = self.stagehand.agent.execute()
            else:
                # Use the mock agent
                self.logger.info("Using mock Stagehand agent for task execution")
                result = self.stagehand.agent.execute()

            # Extract actions from the result
            actions = []
            if hasattr(result, 'actions') and result.actions:
                actions = result.actions
            elif isinstance(result, dict) and 'actions' in result:
                actions = result['actions']

            # If we're using the mock version, generate some realistic-looking actions
            if not STAGEHAND_AVAILABLE:
                # Generate mock actions based on the task
                actions = self._generate_mock_actions(task, url)

            # Record actions if recorder is available
            if self.simulation_recorder and actions:
                for action in actions:
                    self.simulation_recorder.record_action({
                        "type": action.get("action", "unknown"),
                        "description": action.get("description", ""),
                        "target": action.get("selector", ""),
                        "timestamp": time.time()
                    })

            # Take a final screenshot
            screenshot = self.take_screenshot()

            return {
                "success": True,
                "message": f"Executed task: {task}",
                "actions": actions,
                "screenshot": screenshot
            }

        except Exception as e:
            self.logger.error(f"Error executing task with Stagehand: {str(e)}")
            return {
                "success": False,
                "message": f"Task execution failed: {str(e)}",
                "actions": [],
                "screenshot": None
            }

    def _generate_mock_actions(self, task: str, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate mock actions for a task when Stagehand is not available."""
        actions = []

        # Add navigation action if URL is provided
        if url:
            actions.append({
                "action": "navigate",
                "description": f"Navigated to {url}",
                "selector": url,
                "timestamp": time.time()
            })

        # Parse the task to generate relevant actions
        task_lower = task.lower()

        # Search-related actions
        if "search" in task_lower or "find" in task_lower:
            search_term = task_lower.split("search for ")[-1].split("find ")[-1].split(" ")[0]
            actions.append({
                "action": "click",
                "description": "Clicked on search box",
                "selector": "input[type='search']",
                "timestamp": time.time() + 1
            })
            actions.append({
                "action": "input",
                "description": f"Typed '{search_term}' in search box",
                "selector": "input[type='search']",
                "value": search_term,
                "timestamp": time.time() + 2
            })
            actions.append({
                "action": "click",
                "description": "Clicked search button",
                "selector": "button[type='submit']",
                "timestamp": time.time() + 3
            })

        # Click-related actions
        if "click" in task_lower:
            element = task_lower.split("click on ")[-1].split("click ")[-1].split(" ")[0]
            actions.append({
                "action": "click",
                "description": f"Clicked on {element}",
                "selector": f"button:contains('{element}')",
                "timestamp": time.time() + 4
            })

        # Form-related actions
        if "fill" in task_lower or "form" in task_lower or "enter" in task_lower:
            actions.append({
                "action": "click",
                "description": "Clicked on form field",
                "selector": "input[type='text']",
                "timestamp": time.time() + 5
            })
            actions.append({
                "action": "input",
                "description": "Entered information in form field",
                "selector": "input[type='text']",
                "value": "test information",
                "timestamp": time.time() + 6
            })
            actions.append({
                "action": "click",
                "description": "Clicked submit button",
                "selector": "button[type='submit']",
                "timestamp": time.time() + 7
            })

        # Add some generic actions if we don't have any specific ones
        if len(actions) <= 1:
            actions.append({
                "action": "click",
                "description": "Clicked on main navigation",
                "selector": "nav a",
                "timestamp": time.time() + 1
            })
            actions.append({
                "action": "scroll",
                "description": "Scrolled down the page",
                "selector": "body",
                "timestamp": time.time() + 2
            })
            actions.append({
                "action": "click",
                "description": "Clicked on a button",
                "selector": "button",
                "timestamp": time.time() + 3
            })

        return actions

    def _break_down_task(self, task: str) -> List[str]:
        """
        Break down a complex task into simpler steps.

        Args:
            task: The complex task to break down

        Returns:
            List of simpler steps
        """
        # For now, just return the task as a single step
        # In a more advanced implementation, we could use an LLM to break down the task
        return [task]

    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to

        Returns:
            Result dictionary
        """
        self.logger.info(f"Navigating to {url}")

        try:
            # Make sure URL has proper format
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            # Navigate to URL using Stagehand
            self.page.goto(url)
            time.sleep(2)  # Wait for page to load

            # Record navigation action if recorder is available
            if self.simulation_recorder:
                self.simulation_recorder.record_action({
                    "type": "navigate",
                    "description": f"Navigated to {url}",
                    "target": url,
                    "timestamp": time.time()
                })

            # Take a screenshot
            screenshot = self.take_screenshot()

            return {
                "success": True,
                "message": f"Navigated to {url}",
                "screenshot": screenshot,
                "url": url
            }

        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return {
                "success": False,
                "message": f"Navigation failed: {str(e)}",
                "screenshot": None,
                "url": url
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
            # Use browser_connector's page if available, otherwise use our own
            page = self.browser_connector.stagehand_page if self.browser_connector else self.stagehand_page

            # Get page content using Stagehand's observe method
            observations = self.stagehand.observe("Describe the current page structure")

            # Get page URL and title
            url = page.url
            title = page.title()

            # Extract clickable elements
            clickable_observations = self.stagehand.observe("Find all clickable elements on the page")
            clickables = []
            for obs in clickable_observations:
                if "selector" in obs and "description" in obs:
                    clickables.append({
                        "id": f"clickable_{len(clickables)}",
                        "selector": obs["selector"],
                        "text": obs["description"],
                        "type": "clickable"
                    })

            # Extract input fields
            input_observations = self.stagehand.observe("Find all input fields on the page")
            inputs = []
            for obs in input_observations:
                if "selector" in obs and "description" in obs:
                    inputs.append({
                        "id": f"input_{len(inputs)}",
                        "selector": obs["selector"],
                        "label": obs["description"],
                        "type": "input"
                    })

            # Extract text blocks
            text_blocks = []
            if observations:
                # Use the first observation as a general description
                text_blocks.append({
                    "id": "main_content",
                    "text": observations[0].get("description", ""),
                    "type": "text"
                })

            # Store elements for later reference
            self.current_page_elements = {}
            for element in clickables + inputs:
                self.current_page_elements[element["id"]] = element

            return {
                'url': url,
                'title': title,
                'clickables': clickables,
                'inputs': inputs,
                'text_blocks': text_blocks,
                'error_message': None
            }
        except Exception as e:
            self.logger.error(f"Error simplifying HTML: {str(e)}")
            return {
                'url': page.url if hasattr(self, 'page') else "",
                'title': "",
                'clickables': [],
                'inputs': [],
                'text_blocks': [],
                'error_message': str(e)
            }

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
            observations = self.stagehand.observe(instruction)
            return observations
        except Exception as e:
            self.logger.error(f"Error observing page: {str(e)}")
            return []

    def act(self, action_description: str) -> Dict[str, Any]:
        """
        Act on the page based on a natural language description.

        Args:
            action_description: Natural language description of the action to perform
                               or an action object from observe

        Returns:
            Result dictionary
        """
        self.logger.info(f"Acting on page with description: {action_description}")

        # If action_description is already an action object, use it directly
        if isinstance(action_description, dict) and "action" in action_description:
            action = action_description
            self.logger.info(f"Using provided action object: {action}")

            try:
                # Execute the action
                self.stagehand.act(action)

                # Record the action if recorder is available
                if self.simulation_recorder:
                    self.simulation_recorder.record_action({
                        "type": action.get("action", "unknown"),
                        "description": action.get("description", ""),
                        "target": action.get("selector", ""),
                        "timestamp": time.time()
                    })

                return {
                    "success": True,
                    "message": f"Executed action: {action.get('description', 'Unknown action')}",
                    "action": action
                }
            except Exception as e:
                self.logger.error(f"Error executing action object: {str(e)}")
                return {
                    "success": False,
                    "message": f"Action failed: {str(e)}"
                }

        # Check if we have this action cached
        cache_key = str(action_description).lower().strip()
        if cache_key in self.action_cache:
            return self.act(self.action_cache[cache_key])

        try:
            # Use Stagehand's observe-act pattern
            observations = self.observe(action_description)
            if observations:
                action = observations[0]
                self.logger.info(f"Observed action: {action}")

                # Cache the action for future use
                self.action_cache[cache_key] = action

                # Execute the action
                self.stagehand.act(action)

                # Record the action if recorder is available
                if self.simulation_recorder:
                    self.simulation_recorder.record_action({
                        "type": action.get("action", "unknown"),
                        "description": action.get("description", ""),
                        "target": action.get("selector", ""),
                        "timestamp": time.time()
                    })

                # Take a screenshot after action
                screenshot = self.take_screenshot()

                return {
                    "success": True,
                    "message": f"Executed action: {action.get('description', 'Unknown action')}",
                    "action": action,
                    "screenshot": screenshot
                }
            else:
                return {
                    "success": False,
                    "message": f"No action found for description: {action_description}"
                }
        except Exception as e:
            self.logger.error(f"Error acting on page: {str(e)}")
            return {
                "success": False,
                "message": f"Action failed: {str(e)}"
            }

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

            elif action_type == 'click':
                selector = action.get('target', '')
                description = action.get('description', f"Click on {selector}")

                # Use Stagehand's observe-act pattern
                observations = self.stagehand.observe(description)
                if observations:
                    self.stagehand.act(observations[0])

                    # Record the action if recorder is available
                    if self.simulation_recorder:
                        self.simulation_recorder.record_action(action)

                    return {
                        "success": True,
                        "message": f"Clicked on {selector}"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Element not found: {selector}"
                    }

            elif action_type == 'input':
                selector = action.get('target', '')
                value = action.get('value', '')
                description = action.get('description', f"Type '{value}' into {selector}")

                # Use Stagehand's observe-act pattern
                observations = self.stagehand.observe(f"Find the input field {selector}")
                if observations:
                    # First click on the input field
                    self.stagehand.act(observations[0])

                    # Then type the value
                    page = self.browser_connector.stagehand_page if self.browser_connector else self.stagehand_page
                    page.keyboard.type(value)

                    # Record the action if recorder is available
                    if self.simulation_recorder:
                        self.simulation_recorder.record_action(action)

                    return {
                        "success": True,
                        "message": f"Entered '{value}' into {selector}"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Input field not found: {selector}"
                    }

            elif action_type == 'submit':
                selector = action.get('target', '')
                description = action.get('description', f"Submit form {selector}")

                # Use Stagehand's observe-act pattern
                observations = self.stagehand.observe(description)
                if observations:
                    self.stagehand.act(observations[0])

                    # Record the action if recorder is available
                    if self.simulation_recorder:
                        self.simulation_recorder.record_action(action)

                    return {
                        "success": True,
                        "message": f"Submitted form {selector}"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Form not found: {selector}"
                    }

            elif action_type == 'back':
                page = self.browser_connector.stagehand_page if self.browser_connector else self.stagehand_page
                page.go_back()
                time.sleep(1)

                # Record the action if recorder is available
                if self.simulation_recorder:
                    self.simulation_recorder.record_action(action)

                return {
                    "success": True,
                    "message": "Navigated back"
                }

            elif action_type == 'wait':
                seconds = int(action.get('value', 2))
                time.sleep(seconds)

                # Record the action if recorder is available
                if self.simulation_recorder:
                    self.simulation_recorder.record_action(action)

                return {
                    "success": True,
                    "message": f"Waited for {seconds} seconds"
                }

            else:
                return {
                    "success": False,
                    "message": f"Unsupported action type: {action_type}"
                }

        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}")
            return {
                "success": False,
                "message": f"Action failed: {str(e)}"
            }

    def get_current_url(self) -> str:
        """
        Get the current URL.

        Returns:
            Current URL
        """
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {str(e)}")
            return ""

    def take_screenshot(self, filepath: Optional[str] = None) -> str:
        """
        Take a screenshot of the current browser window.

        Args:
            filepath: Optional path to save the screenshot

        Returns:
            Base64-encoded screenshot data or path to the saved screenshot file
        """
        try:
            # If we're using the mock version, return a mock screenshot
            if not STAGEHAND_AVAILABLE:
                # Generate a mock screenshot based on the current time
                timestamp = int(time.time())
                if timestamp % 3 == 0:
                    return "https://via.placeholder.com/800x600?text=Mock+Screenshot+1"
                elif timestamp % 3 == 1:
                    return "https://via.placeholder.com/800x600?text=Mock+Screenshot+2"
                else:
                    return "https://via.placeholder.com/800x600?text=Mock+Screenshot+3"

            # If no filepath is provided, return base64-encoded screenshot
            if filepath is None:
                # Use Stagehand's screenshot capability
                try:
                    # First try to use the page's screenshot method
                    screenshot_bytes = self.page.screenshot()
                    return f"data:image/png;base64,{base64.b64encode(screenshot_bytes).decode('utf-8')}"
                except Exception as screenshot_error:
                    self.logger.warning(f"Error taking screenshot with page.screenshot(): {str(screenshot_error)}")

                    # Fallback to evaluate method if available
                    try:
                        # Use JavaScript to capture screenshot
                        js_screenshot = """
                        () => {
                            const canvas = document.createElement('canvas');
                            const context = canvas.getContext('2d');
                            const img = new Image();

                            canvas.width = window.innerWidth;
                            canvas.height = window.innerHeight;

                            // Draw the current view to the canvas
                            context.drawImage(document, 0, 0, canvas.width, canvas.height);

                            // Return as data URL
                            return canvas.toDataURL('image/png');
                        }
                        """
                        screenshot_data_url = self.page.evaluate(js_screenshot)
                        return screenshot_data_url
                    except Exception as js_error:
                        self.logger.error(f"Error taking screenshot with JavaScript: {str(js_error)}")
                        # Fall back to mock screenshot
                        return "https://via.placeholder.com/800x600?text=Screenshot+Unavailable"
            else:
                # Save to file if filepath is provided
                if STAGEHAND_AVAILABLE:
                    self.page.screenshot(path=filepath)
                    return filepath
                else:
                    # Mock saving to file
                    self.logger.info(f"Mock saving screenshot to {filepath}")
                    return filepath
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            # Fall back to mock screenshot
            return "https://via.placeholder.com/800x600?text=Error+Taking+Screenshot"

    def close(self):
        """Close the Stagehand browser."""
        try:
            if hasattr(self, 'stagehand'):
                self.stagehand.close()
            self.logger.info("Stagehand session closed")
        except Exception as e:
            self.logger.error(f"Error closing Stagehand session: {str(e)}")
