
# UXAgent Backend

This is the backend implementation of UXAgent, providing capabilities for:

1. Memory Stream - A central memory repository for the agent
2. Universal Browser Connector - Simplifies web interaction for LLMs
3. LLM Agent - Orchestrates perception, planning, action, reflection, and wonder modules
4. Persona Generator - Creates realistic user personas

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. Run the API server:
```bash
python api.py
```

## API Endpoints

The API will be available at http://localhost:8000 with the following endpoints:

- `POST /api/config/apikey` - Set API key for LLM provider
- `GET /api/config/providers` - Get configured LLM providers
- `POST /api/personas/generate` - Generate personas using LLM
- `POST /api/simulations/start` - Start a new simulation
- `GET /api/simulations/{simulation_id}/status` - Get simulation status
- `GET /api/simulations/{simulation_id}` - Get simulation result
- `GET /api/simulations` - List all simulations
- `POST /api/interview/{simulation_id}` - Interview the agent about their experience

## Frontend Integration

To integrate with the React frontend:
1. Make sure this backend service is running
2. Update the API service in the frontend to point to this backend
3. Configure your OpenAI API key in the settings page

## Customizing the Agent

The LLM Agent operates using a two-loop architecture:

1. Fast Loop: Perception → Planning → Action
2. Slow Loop: Reflection → Wonder

You can customize the behavior by modifying the weights used for memory retrieval in each module.
