# UX Agent Simulator

A simulation framework for UX research using AI agents with a two-loop architecture.

## Overview

The UX Agent Simulator is a powerful tool for UX researchers to simulate user interactions with websites and applications. It uses a two-loop architecture with LLMs to create realistic user simulations that can help identify usability issues and gather insights.

## Key Features

- **Two-Loop Architecture**: Fast loop (Perception → Planning → Action) and Slow loop (Reflection, Wonder) for realistic user simulation
- **Memory Stream**: Sophisticated memory system with importance, relevance, and recency scoring
- **Stagehand Integration**: Universal Browser Controller using Stagehand for robust web interaction
- **Simulation Recording & Replay**: Record and replay user sessions for analysis
- **Agent Interview Interface**: Interview simulated users about their experience
- **Persona Generation**: Create diverse user personas for testing

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for GPT-4o)
- Browserbase API key (optional, for cloud-based browser automation)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alhridoy/ux_alpha.git
   cd ux_alpha
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Update your API keys in the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   BROWSERBASE_API_KEY=your_browserbase_api_key_here (optional)
   BROWSERBASE_PROJECT_ID=your_browserbase_project_id_here (optional)
   ```

### Running the Demo

Try the Stagehand demo to see the Universal Browser Controller in action:

```bash
python examples/stagehand_demo.py
```

### Starting the API Server

Start the API server to use the full UX Agent Simulator:

```bash
python src/backend/api.py
```

The API will be available at: http://localhost:8000

## Using Stagehand as a Universal Browser Controller

Stagehand is a powerful browser automation framework that serves as the Universal Browser Controller in the UX Agent Simulator. It provides a natural language interface to browser automation, making it perfect for AI agent interactions.

### Key Capabilities

1. **Observe-Act-Extract Pattern**:
   - **Observe**: Find potential actions on a page
   - **Act**: Execute actions based on natural language instructions
   - **Extract**: Retrieve structured data from web pages

2. **Action Caching**: Reduce redundant LLM calls by caching actions

3. **Computer Use Agents**: Handle complex tasks with specialized agents

4. **Browserbase Integration**: Optional cloud-based browser automation

### Example Usage

```python
from src.backend.universal_browser_connector import UniversalBrowserConnector

# Initialize the browser connector
browser = UniversalBrowserConnector(
    headless=False,
    stagehand_api_key="your_openai_api_key_here"
)

# Navigate to a website
browser.navigate("https://example.com")

# Observe the page
observations = browser.observe("Find all clickable elements on this page")

# Act on the page
browser.act("Click on the 'About' link")

# Extract data from the page
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

# Execute a complex task
browser.execute_complex_task(
    "Find information about the company and summarize it"
)

# Close the browser
browser.close()
```

## Architecture

The UX Agent Simulator follows a two-loop architecture:

### Fast Loop

- **Perception Module**: Observes the current web page
- **Planning Module**: Creates and updates plans based on observations
- **Action Module**: Translates plans into specific actions

### Slow Loop

- **Reflection Module**: Generates insights based on recent experiences
- **Wonder Module**: Creates spontaneous thoughts for more realistic simulation

### Memory Stream

The Memory Stream is the central component that stores and retrieves memories based on:

- **Importance**: How important a memory is to the agent's goals
- **Relevance**: How relevant a memory is to the current context
- **Recency**: How recent a memory is
