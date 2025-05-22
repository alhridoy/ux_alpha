"""
Stagehand Demo for UX Agent Simulator.
This script demonstrates how to use Stagehand as a Universal Browser Controller.
"""

import os
import sys
import time
import json
import logging
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the Universal Browser Connector
from src.backend.universal_browser_connector import UniversalBrowserConnector
from src.backend.simulation_recorder import SimulationRecorder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

def main():
    """Run the Stagehand demo."""
    # Get API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable must be set")
        return
    
    # Initialize the Universal Browser Connector
    print("Initializing Universal Browser Connector with Stagehand...")
    browser = UniversalBrowserConnector(
        headless=False,
        stagehand_api_key=openai_api_key
    )
    
    # Initialize the Simulation Recorder
    recorder = SimulationRecorder(browser)
    recorder.start_recording()
    
    try:
        # Navigate to a website
        print("\nNavigating to example.com...")
        browser.navigate("https://example.com")
        
        # Observe the page
        print("\nObserving the page...")
        observations = browser.observe("Find all clickable elements on this page")
        print(f"Found {len(observations)} potential actions:")
        for i, obs in enumerate(observations):
            print(f"  {i+1}. {obs.get('description', 'Unknown')}")
        
        # Extract data from the page
        print("\nExtracting data from the page...")
        data = browser.extract_data(
            "Extract the main heading and paragraph text from this page",
            {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "paragraph": {"type": "string"}
                }
            }
        )
        
        if data.get('success', False):
            print("Extracted data:")
            print(f"  Heading: {data.get('data', {}).get('heading', 'Not found')}")
            print(f"  Paragraph: {data.get('data', {}).get('paragraph', 'Not found')}")
        else:
            print(f"Failed to extract data: {data.get('message', 'Unknown error')}")
        
        # Take a screenshot
        print("\nTaking a screenshot...")
        screenshot_path = browser.take_screenshot("example_screenshot.png")
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Navigate to a more complex website
        print("\nNavigating to a more complex website (Wikipedia)...")
        browser.navigate("https://en.wikipedia.org/wiki/Main_Page")
        
        # Use the act method to perform an action
        print("\nPerforming a search action...")
        browser.act("Search for 'artificial intelligence'")
        
        # Wait for the page to load
        time.sleep(2)
        
        # Extract data from the search results
        print("\nExtracting search results...")
        search_results = browser.extract_data(
            "Extract the first 3 search result titles",
            {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        )
        
        if search_results.get('success', False):
            print("Search results:")
            for i, result in enumerate(search_results.get('data', {}).get('results', [])):
                print(f"  {i+1}. {result}")
        else:
            print(f"Failed to extract search results: {search_results.get('message', 'Unknown error')}")
        
        # Execute a complex task
        print("\nExecuting a complex task...")
        complex_result = browser.execute_complex_task(
            "Find information about the history of artificial intelligence and summarize it in 3 bullet points"
        )
        
        if complex_result.get('success', False):
            print("Complex task result:")
            print(f"  {complex_result.get('message', 'No message')}")
        else:
            print(f"Failed to execute complex task: {complex_result.get('message', 'Unknown error')}")
        
        # Stop recording
        print("\nStopping recording...")
        action_trace = recorder.stop_recording()
        
        # Save the trace
        trace_path = "example_trace.json"
        recorder.save_trace(trace_path)
        print(f"Action trace saved to: {trace_path}")
        
        # Replay the trace
        print("\nReplaying the action trace...")
        replay_result = recorder.replay_trace(delay=1.0, highlight=True)
        
        if replay_result.get('success', False):
            print(f"Replay completed: {replay_result.get('message', '')}")
        else:
            print(f"Replay failed: {replay_result.get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the browser
        browser.close()
        print("\nDemo completed!")

if __name__ == "__main__":
    main()
