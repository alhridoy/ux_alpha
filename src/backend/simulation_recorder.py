"""
Simulation Recorder for UX Agent Simulator.
This module provides functionality to record and replay simulation sessions.
It also supports live browser updates during simulations.
"""

import time
import json
import logging
import base64
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class SimulationRecorder:
    """Records and replays simulation sessions."""

    def __init__(self, browser_connector=None, memory_stream=None):
        """
        Initialize the recorder.

        Args:
            browser_connector: UniversalBrowserConnector or StagehandAgent instance
            memory_stream: Optional MemoryStream instance
        """
        self.browser_connector = browser_connector
        self.memory_stream = memory_stream
        self.recording = False
        self.action_trace = []
        self.logger = logging.getLogger(__name__)

        # Live browser update tracking
        self.current_simulation_id = None
        self.simulation_start_time = None
        self.last_screenshot = None
        self.current_progress = 0
        self.current_action = "Initializing"

    def start_recording(self, simulation_id: str = None) -> None:
        """
        Start recording a simulation session.

        Args:
            simulation_id: Optional ID for the simulation
        """
        self.recording = True
        self.action_trace = []
        self.current_simulation_id = simulation_id
        self.simulation_start_time = time.time()
        self.current_progress = 0
        self.current_action = "Initializing simulation"
        self.logger.info(f"Started recording simulation session {simulation_id}")

    def stop_recording(self) -> List[Dict[str, Any]]:
        """
        Stop recording and return the action trace.

        Returns:
            List of recorded actions
        """
        self.recording = False
        self.logger.info(f"Stopped recording. Recorded {len(self.action_trace)} actions")
        return self.action_trace

    def record_action(self, action: Dict[str, Any]) -> None:
        """
        Record an action in the trace.

        Args:
            action: Action object
        """
        if self.recording:
            # Add timestamp
            current_time = time.time()
            action_with_timestamp = {
                **action,
                'timestamp': current_time
            }
            self.action_trace.append(action_with_timestamp)

            # Update progress and current action for live updates
            self._update_simulation_progress(action)

            # Try to capture a screenshot if possible
            self._capture_screenshot()

            # Also record in memory stream if available
            if self.memory_stream:
                self._add_to_memory_stream(action)

    def _add_to_memory_stream(self, action: Dict[str, Any]) -> None:
        """
        Add an action to the memory stream.

        Args:
            action: Action object
        """
        action_description = action.get('description', 'Unknown action')
        action_type = action.get('type', 'unknown')

        self.memory_stream.add_memory(
            memory_type="action_taken",
            content=f"Performed {action_type} action: {action_description}",
            source_module="SimulationRecorder",
            importance_score=7.0,  # Actions are typically important
            metadata=action  # Store the full action for replay
        )

    def save_trace(self, filepath: str) -> None:
        """
        Save the action trace to a file.

        Args:
            filepath: Path to save the trace
        """
        with open(filepath, 'w') as f:
            json.dump(self.action_trace, f, indent=2)
        self.logger.info(f"Saved action trace to {filepath}")

    def load_trace(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load an action trace from a file.

        Args:
            filepath: Path to load the trace from

        Returns:
            List of actions
        """
        with open(filepath, 'r') as f:
            self.action_trace = json.load(f)
        self.logger.info(f"Loaded action trace from {filepath} with {len(self.action_trace)} actions")
        return self.action_trace

    def replay_trace(self,
                    trace: Optional[List[Dict[str, Any]]] = None,
                    delay: float = 1.0,
                    highlight: bool = True) -> Dict[str, Any]:
        """
        Replay an action trace.

        Args:
            trace: Action trace to replay (uses loaded trace if None)
            delay: Delay between actions in seconds
            highlight: Whether to highlight elements before acting

        Returns:
            Result dictionary
        """
        if trace is None:
            trace = self.action_trace

        if not trace:
            return {'success': False, 'message': 'No actions to replay'}

        results = []

        # Start with the initial URL if it's a navigation action
        initial_action = trace[0]
        if initial_action.get('type') == 'navigate':
            url = initial_action.get('target', '')
            self.browser_connector.navigate(url)

        # Replay each action
        for i, action in enumerate(trace):
            self.logger.info(f"Replaying action {i+1}/{len(trace)}: {action.get('description', 'Unknown action')}")

            if highlight and action.get('selector'):
                # Highlight the element before acting (if possible)
                self._highlight_element(action.get('selector'))

            # Execute the action
            result = self.browser_connector.execute_action(action)
            results.append(result)

            # Wait between actions
            time.sleep(delay)

        return {
            'success': True,
            'message': f'Replayed {len(trace)} actions',
            'results': results
        }

    def _highlight_element(self, selector: str) -> None:
        """
        Highlight an element in the browser.

        Args:
            selector: Element selector
        """
        try:
            # Use JavaScript to highlight the element
            script = """
            (selector) => {
                const element = document.querySelector(selector);
                if (element) {
                    const originalBackground = element.style.backgroundColor;
                    const originalBorder = element.style.border;

                    element.style.backgroundColor = 'yellow';
                    element.style.border = '2px solid red';

                    setTimeout(() => {
                        element.style.backgroundColor = originalBackground;
                        element.style.border = originalBorder;
                    }, 1000);

                    return true;
                }
                return false;
            }
            """
            self.browser_connector.stagehand_page.evaluate(script, selector)
        except Exception as e:
            self.logger.error(f"Error highlighting element: {str(e)}")

    def _update_simulation_progress(self, action: Dict[str, Any]) -> None:
        """
        Update the simulation progress based on the current action.

        Args:
            action: The current action being performed
        """
        if not self.recording or not self.current_simulation_id:
            return

        # Calculate progress based on number of actions and time elapsed
        action_count = len(self.action_trace)

        # Estimate progress (this is a simplified approach)
        if action_count <= 1:
            self.current_progress = 10  # Just started
        elif action_count <= 3:
            self.current_progress = 30  # Early progress
        elif action_count <= 5:
            self.current_progress = 50  # Mid progress
        elif action_count <= 8:
            self.current_progress = 70  # Good progress
        elif action_count <= 10:
            self.current_progress = 90  # Almost done
        else:
            self.current_progress = 95  # Finishing up

        # Update current action description
        action_type = action.get('type', 'unknown')
        action_description = action.get('description', '')
        target = action.get('target', '')

        if action_type == 'navigate':
            self.current_action = f"Navigating to {target}"
        elif action_type == 'click':
            self.current_action = f"Clicking on {target}"
        elif action_type == 'input':
            self.current_action = f"Entering text in {target}"
        elif action_type == 'scroll':
            self.current_action = f"Scrolling the page"
        elif action_type == 'wait':
            self.current_action = f"Waiting for page to load"
        else:
            self.current_action = action_description or f"Performing {action_type} action"

    def _capture_screenshot(self) -> None:
        """Capture a screenshot of the current browser state."""
        try:
            # Try to get screenshot from browser_connector or agent
            if self.browser_connector:
                if hasattr(self.browser_connector, 'take_screenshot'):
                    # Get base64-encoded screenshot from browser_connector
                    screenshot_data = self.browser_connector.take_screenshot()
                    if screenshot_data and isinstance(screenshot_data, str):
                        # Store the screenshot data URL
                        self.last_screenshot = screenshot_data
                        self.logger.info("Successfully captured screenshot from browser_connector")
                        return
                elif hasattr(self.browser_connector, 'stagehand_page'):
                    # Get screenshot directly from the page
                    page = self.browser_connector.stagehand_page
                    screenshot_bytes = page.screenshot()
                    self.last_screenshot = f"data:image/png;base64,{base64.b64encode(screenshot_bytes).decode('utf-8')}"
                    self.logger.info("Successfully captured screenshot from stagehand_page")
                    return

            # If we get here, we couldn't get a screenshot
            self.logger.warning("No method available to capture screenshot")
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {str(e)}")

    def get_live_update(self) -> Dict[str, Any]:
        """
        Get the current state of the simulation for live updates.

        Returns:
            Dictionary with current simulation state
        """
        # Capture a new screenshot
        self._capture_screenshot()

        if not self.current_simulation_id:
            return {
                'success': False,
                'message': 'No active simulation'
            }

        # Get the current URL
        current_url = ""
        if self.browser_connector and hasattr(self.browser_connector, 'get_current_url'):
            current_url = self.browser_connector.get_current_url()

        return {
            'success': True,
            'simulationId': self.current_simulation_id,
            'progress': self.current_progress,
            'currentAction': self.current_action,
            'screenshot': self.last_screenshot,
            'currentUrl': current_url,
            'actionCount': len(self.action_trace),
            'timestamp': int(time.time() * 1000)
        }
