# Stagehand Integration for UX Agent Simulator

This document explains how to set up and use the Stagehand integration for the UX Agent Simulator.

## Overview

The UX Agent Simulator now uses Stagehand for browser automation. Stagehand is an AI-powered browser automation tool that provides a more natural way to interact with web pages. The integration allows the UX Agent to control the browser directly within the simulation interface, rather than opening a separate browser window.

## Requirements

- Python 3.9+
- Stagehand API key (from [stagehand.dev](https://stagehand.dev))
- OpenAI API key (for the LLM that powers Stagehand)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install
```

## Configuration

1. Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
STAGEHAND_API_KEY=your_stagehand_api_key
```

2. Start the backend server:

```bash
cd src/backend
uvicorn simple_api:app --reload
```

3. Start the frontend development server (in a separate terminal):

```bash
npm run dev
```

## Using Stagehand in the UX Agent Simulator

1. Open the UX Agent Simulator in your browser.
2. Navigate to the Simulations page.
3. Create a new simulation.
4. In the Browser Automation section, you'll see a "Configure Stagehand API Key" button if Stagehand is not yet configured.
5. Click the button and enter your Stagehand API key.
6. Start the simulation.

The browser view will now show the actual browser being controlled by Stagehand, rather than opening a separate window.

## How It Works

The integration uses Stagehand's LOCAL environment setting to control the browser directly within the UX Agent Simulator interface. This is achieved through the following components:

1. **StagehandAgent**: A Python class that wraps the Stagehand API and provides methods for browser automation.
2. **LiveBrowserView**: A React component that displays the browser view and updates it in real-time.
3. **API Endpoints**: FastAPI endpoints that handle Stagehand initialization, navigation, action execution, and screenshot capture.

## Troubleshooting

If you encounter issues with the Stagehand integration, try the following:

1. Check that your API keys are correctly set in the `.env` file.
2. Make sure you have installed all the required dependencies.
3. Check the browser console and server logs for error messages.
4. Try restarting both the frontend and backend servers.

## API Reference

The following API endpoints are available for Stagehand integration:

- `POST /api/stagehand/init`: Initialize Stagehand
- `POST /api/stagehand/navigate`: Navigate to a URL
- `POST /api/stagehand/execute`: Execute an action
- `POST /api/stagehand/screenshot`: Take a screenshot
- `POST /api/stagehand/extract`: Extract data from the page
- `POST /api/stagehand/close`: Close the Stagehand session
- `GET /api/stagehand/live/{simulation_id}`: Get live updates for a simulation

## Credits

This integration uses [stagehand-py](https://pypi.org/project/stagehand-py/), the Python SDK for Stagehand.
