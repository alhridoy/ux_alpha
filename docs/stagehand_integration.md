# Stagehand Integration Guide

This guide explains how to use Stagehand as a Universal Browser Controller in the UX Agent Simulator.

## What is Stagehand?

[Stagehand](https://docs.stagehand.dev/) is a powerful browser automation framework that provides a natural language interface to browser automation. It's built on top of Playwright and uses LLMs to translate natural language instructions into browser actions.

## Why Stagehand for UX Agent Simulator?

Stagehand is an excellent choice for the UX Agent Simulator for several reasons:

1. **Natural Language Interface**: Stagehand allows agents to interact with web pages using natural language, which aligns perfectly with the LLM-based architecture of the UX Agent Simulator.

2. **Observe-Act-Extract Pattern**: This pattern maps directly to the Perception → Planning → Action loop in the UX Agent Simulator.

3. **Resilience to DOM Changes**: Stagehand is designed to be resilient to unpredictable DOM changes, making it ideal for testing on websites you don't control.

4. **Action Caching**: Stagehand supports caching actions to reduce redundant LLM calls, which improves performance and reduces costs.

5. **Computer Use Agents**: Stagehand supports specialized agents for complex tasks, which can enhance the capabilities of the UX Agent Simulator.

## Installation

Stagehand requires the following dependencies:

```bash
pip install browserbasehq-stagehand playwright
playwright install
```

## Core Concepts

### Observe

The `observe` method is used to find potential actions on a page. It returns an array of potential actions with selectors and descriptions.

```python
observations = browser.observe("Find the search box on this page")
```

### Act

The `act` method is used to execute an action on the page. It can take either a natural language description or an action object returned by `observe`.

```python
# Using a natural language description
browser.act("Click on the search button")

# Using an action object from observe
observations = browser.observe("Find the search button")
browser.act(observations[0])
```

### Extract

The `extract` method is used to extract structured data from a page using a schema.

```python
data = browser.extract_data(
    "Extract the product name and price",
    {
        "type": "object",
        "properties": {
            "productName": {"type": "string"},
            "price": {"type": "string"}
        },
        "required": ["productName", "price"]
    }
)
```

## Enhanced Universal Browser Connector

The UX Agent Simulator includes an enhanced Universal Browser Connector that leverages Stagehand's capabilities. Here's how to use it:

### Initialization

```python
from src.backend.universal_browser_connector import UniversalBrowserConnector

# Initialize with local browser
browser = UniversalBrowserConnector(
    headless=False,
    stagehand_api_key="your_openai_api_key_here"
)

# Initialize with Browserbase (cloud browser)
browser = UniversalBrowserConnector(
    use_browserbase=True,
    browserbase_api_key="your_browserbase_api_key_here",
    browserbase_project_id="your_browserbase_project_id_here",
    stagehand_api_key="your_openai_api_key_here"
)
```

### Navigation

```python
# Navigate to a URL
browser.navigate("https://example.com")
```

### Observation

```python
# Observe the page
observations = browser.observe("Find all clickable elements on this page")

# Print observations
for obs in observations:
    print(f"Description: {obs.get('description')}")
    print(f"Selector: {obs.get('selector')}")
```

### Action

```python
# Act with a natural language description
browser.act("Click on the 'About' link")

# Act with caching to reduce redundant LLM calls
browser.act_with_cache("Click on the 'About' link")

# Execute a structured action
action = {
    'type': 'click',
    'name': 'about_link',
    'description': 'Click on the About link'
}
browser.execute_action(action)
```

### Data Extraction

```python
# Extract structured data
data = browser.extract_data(
    "Extract the main heading and paragraph text",
    {
        "type": "object",
        "properties": {
            "heading": {"type": "string"},
            "paragraph": {"type": "string"}
        }
    }
)

# Access extracted data
if data.get('success', False):
    heading = data.get('data', {}).get('heading', '')
    paragraph = data.get('data', {}).get('paragraph', '')
```

### Complex Tasks

```python
# Execute a complex task using a computer use agent
result = browser.execute_complex_task(
    "Find information about the company and summarize it"
)
```

### Screenshots

```python
# Take a screenshot
screenshot_path = browser.take_screenshot("screenshot.png")
```

### Cleanup

```python
# Close the browser
browser.close()
```

## Simulation Recording and Replay

The UX Agent Simulator includes a Simulation Recorder that can record and replay user sessions:

```python
from src.backend.simulation_recorder import SimulationRecorder

# Initialize the recorder
recorder = SimulationRecorder(browser)

# Start recording
recorder.start_recording()

# ... perform actions ...

# Stop recording
action_trace = recorder.stop_recording()

# Save the trace
recorder.save_trace("simulation_trace.json")

# Load a trace
recorder.load_trace("simulation_trace.json")

# Replay a trace
recorder.replay_trace(delay=1.0, highlight=True)
```

## Integration with Memory Stream

The Universal Browser Connector can be integrated with the Memory Stream to store observations and actions:

```python
# Observe and add to memory stream
observations = browser.observe("Find all clickable elements on this page")
for obs in observations:
    memory_stream.add_memory(
        memory_type="observation",
        content=f"Observed {obs.get('description', 'element')}",
        source_module="UniversalBrowserConnector",
        importance_score=5.0
    )

# Act and add to memory stream
result = browser.act("Click on the 'About' link")
memory_stream.add_memory(
    memory_type="action_taken",
    content="Clicked on the 'About' link",
    source_module="UniversalBrowserConnector",
    importance_score=7.0
)
```

## Best Practices

1. **Use Caching**: Use `act_with_cache` instead of `act` to reduce redundant LLM calls.

2. **Handle Errors**: Always handle errors when using Stagehand, as web pages can be unpredictable.

3. **Wait for Page Loads**: Add appropriate delays after actions that trigger page loads.

4. **Use Descriptive Instructions**: Be specific in your instructions to Stagehand to get better results.

5. **Extract Structured Data**: Use the `extract_data` method to get structured data instead of parsing HTML manually.

## Troubleshooting

### Common Issues

1. **Element Not Found**: If Stagehand can't find an element, try using a more specific description or wait for the page to load completely.

2. **API Key Issues**: Make sure your OpenAI API key has sufficient credits and permissions.

3. **Browser Crashes**: If the browser crashes, try running in non-headless mode for debugging.

### Debugging

1. **Enable Logging**: Set up logging to see what's happening behind the scenes.

2. **Take Screenshots**: Use `take_screenshot` to capture the state of the page for debugging.

3. **Check Observations**: Print the observations to see what Stagehand is detecting on the page.

## Resources

- [Stagehand Documentation](https://docs.stagehand.dev/)
- [Browserbase Documentation](https://docs.browserbase.com/)
- [Playwright Documentation](https://playwright.dev/)
