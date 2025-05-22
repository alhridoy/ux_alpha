# UX Agent Simulator Setup Instructions

This document provides instructions on how to set up and run the UX Agent Simulator application.

## Overview

The UX Agent Simulator is a tool for UX researchers to simulate user interactions with websites and applications. It uses a two-loop architecture with LLMs to create realistic user simulations that can help identify usability issues and gather insights.

## Prerequisites

- Python 3.8+
- Node.js and npm
- OpenAI API key

## Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install fastapi==0.110.0 uvicorn==0.29.0 beautifulsoup4==4.12.2 openai python-dotenv
   ```

4. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"  # On Windows: set OPENAI_API_KEY=your-openai-api-key
   ```

5. Start the backend server:
   ```bash
   python simple_api.py
   ```

   The backend server will be available at http://localhost:8000.

### 2. Frontend Setup

1. Navigate to the project root directory:
   ```bash
   cd /path/to/ux-agent-sim
   ```

2. Install the frontend dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at http://localhost:8080.

## Using the Application

1. Open your browser and navigate to http://localhost:8080.

2. The application will automatically use the OpenAI API key you set in the backend.

3. You can now:
   - Create and manage personas
   - Run simulations
   - Interview AI agents
   - View simulation results

## Important Notes

- The application uses a simplified backend that doesn't require Stagehand API keys.
- The browser automation is simulated for demonstration purposes.
- For a production environment, you would need to implement actual browser automation using Stagehand or another tool.

## Troubleshooting

If you encounter any issues:

1. Make sure both the backend and frontend servers are running.
2. Check that your OpenAI API key is valid and has sufficient credits.
3. Check the console logs for any error messages.
4. Make sure the ports 8000 and 8080 are not being used by other applications.

## Additional Resources

- [UX Agent Simulator Documentation](https://github.com/yourusername/ux-agent-sim)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
