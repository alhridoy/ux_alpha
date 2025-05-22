"""
Selenium-based browser automation for UX Agent Simulator.
This module provides a fallback when Stagehand is not available.
"""

import os
import time
import logging
import base64
from typing import Dict, List, Any, Optional, Union
import traceback

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
    print("Successfully imported Selenium")
except ImportError as e:
    print(f"Error importing Selenium: {str(e)}")
    SELENIUM_AVAILABLE = False

class SeleniumBrowser:
    """
    A Selenium-based browser automation class.
    This class provides a fallback when Stagehand is not available.
    """

    def __init__(self,
                simulation_recorder=None,
                headless: bool = False,
                api_key: Optional[str] = None):
        """
        Initialize the Selenium browser.

        Args:
            simulation_recorder: Optional SimulationRecorder instance
            headless: Whether to run the browser in headless mode
            api_key: Not used for Selenium, but kept for compatibility
        """
        self.simulation_recorder = simulation_recorder
        self.headless = headless
        self.logger = logging.getLogger(__name__)

        # Check if Selenium is available
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium is not available. Please install it with 'pip install selenium'")
            raise ImportError("Selenium is not available")

        # Initialize Selenium
        self._initialize_selenium()

    def _initialize_selenium(self):
        """Initialize Selenium for browser automation."""
        try:
            self.logger.info("Initializing Selenium...")

            # Set up Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            # Initialize the browser
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)

            self.logger.info("Selenium initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Selenium: {str(e)}")
            traceback.print_exc()
            raise

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

            # Navigate to URL
            self.driver.get(url)
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
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Navigation failed: {str(e)}",
                "screenshot": None,
                "url": url
            }

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
                screenshot_bytes = self.driver.get_screenshot_as_png()
                # Convert to base64
                base64_screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
                # Return as data URL
                return f"data:image/png;base64,{base64_screenshot}"
            else:
                # Save to file if filepath is provided
                self.driver.save_screenshot(filepath)
                return filepath
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            traceback.print_exc()
            return ""

    def get_current_url(self) -> str:
        """
        Get the current URL.

        Returns:
            Current URL
        """
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {str(e)}")
            return ""

    def execute_task(self, task: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using Selenium.
        This is a simplified implementation that just performs basic actions.

        Args:
            task: Natural language description of the task to perform
            url: Optional URL to navigate to before executing the task

        Returns:
            Result dictionary with task execution details
        """
        self.logger.info(f"Executing task: {task}")

        try:
            # Navigate to URL if provided
            if url:
                self.navigate(url)

            # Start recording if recorder is available
            if self.simulation_recorder:
                self.simulation_recorder.start_recording()

            # Perform some basic actions based on the task
            actions = []

            # Search for something if the task mentions search
            if "search" in task.lower():
                search_term = task.split("search for ")[-1].split(" ")[0]
                try:
                    # Try to find a search box
                    search_box = self.driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[name='q'], input[name='search']")
                    search_box.send_keys(search_term)
                    search_box.submit()

                    # Record the action
                    search_action = {
                        "type": "input",
                        "description": f"Searched for {search_term}",
                        "target": "search_box",
                        "timestamp": time.time()
                    }
                    actions.append(search_action)

                    # Record action if recorder is available
                    if self.simulation_recorder:
                        self.simulation_recorder.record_action(search_action)

                    time.sleep(2)  # Wait for search results
                except Exception as e:
                    self.logger.error(f"Error performing search: {str(e)}")

            # Click on a link if the task mentions click
            if "click" in task.lower():
                try:
                    # Try to find a relevant link
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links[:5]:  # Look at first 5 links
                        if link.is_displayed() and link.text:
                            link.click()

                            # Record the action
                            click_action = {
                                "type": "click",
                                "description": f"Clicked on {link.text}",
                                "target": "link",
                                "timestamp": time.time()
                            }
                            actions.append(click_action)

                            # Record action if recorder is available
                            if self.simulation_recorder:
                                self.simulation_recorder.record_action(click_action)

                            time.sleep(2)  # Wait for page to load
                            break
                except Exception as e:
                    self.logger.error(f"Error clicking link: {str(e)}")

            # Take a final screenshot
            screenshot = self.take_screenshot()

            return {
                "success": True,
                "message": f"Executed task: {task}",
                "actions": actions,
                "screenshot": screenshot
            }

        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Task execution failed: {str(e)}",
                "actions": [],
                "screenshot": None
            }

    def close(self):
        """Close the Selenium browser."""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            self.logger.info("Selenium browser closed")
        except Exception as e:
            self.logger.error(f"Error closing Selenium browser: {str(e)}")
            traceback.print_exc()
