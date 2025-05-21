
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from typing import Dict, List, Any, Optional
import uuid
import time
from datetime import datetime
import json
import os

from memory_stream import MemoryStream
from universal_browser_connector import UniversalBrowserConnector
from llm_agent import LLMAgent
from persona_generator import PersonaGenerator

# Initialize FastAPI app
app = FastAPI(title="UXAgent API", description="API for UXAgent browser automation and simulation")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for active sessions and results
active_simulations = {}
simulation_results = {}
browser_connectors = {}
memory_streams = {}

# Models for API requests and responses
class Persona(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    gender: str
    occupation: str
    techExperience: str
    traits: List[str]
    goals: List[str]
    painPoints: List[str]
    profileImage: Optional[str] = None

class SimulationRequest(BaseModel):
    personaId: str
    webUrl: str
    task: str
    maxCycles: Optional[int] = 15
    settings: Optional[Dict[str, Any]] = None

class ApiKeyConfig(BaseModel):
    provider: str
    key: str
    model: Optional[str] = None

# Storage for API keys
api_keys = {}

@app.post("/api/config/apikey")
async def set_api_key(config: ApiKeyConfig):
    """Set API key for an LLM provider"""
    api_keys[config.provider] = {
        "key": config.key,
        "model": config.model or "gpt-4o"
    }
    return {"success": True, "message": f"API key for {config.provider} has been set"}

@app.get("/api/config/providers")
async def get_providers():
    """Get configured LLM providers"""
    return {"providers": list(api_keys.keys())}

@app.post("/api/personas/generate")
async def generate_personas(count: int = 1, config: Optional[Dict[str, Any]] = None):
    """Generate personas using LLM"""
    if "openai" not in api_keys:
        return {"success": False, "message": "OpenAI API key not configured", "personas": []}
    
    try:
        generator = PersonaGenerator(
            api_key=api_keys["openai"]["key"],
            model_name=api_keys["openai"].get("model", "gpt-4o")
        )
        
        raw_personas = generator.generate_multiple_personas(count, config)
        
        # Convert to the expected format
        personas = []
        for raw in raw_personas:
            persona = Persona(
                name=raw["name"],
                age=raw["age"],
                gender=raw["gender"],
                occupation=raw["occupation"],
                techExperience=raw["techExperience"],
                traits=raw.get("traits", []),
                goals=raw.get("goals", []),
                painPoints=raw.get("painPoints", []),
                profileImage=f"https://i.pravatar.cc/150?u={uuid.uuid4()}"
            )
            personas.append(persona.model_dump())
        
        return {"success": True, "personas": personas}
        
    except Exception as e:
        return {"success": False, "message": str(e), "personas": []}

@app.post("/api/simulations/start")
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """Start a new simulation"""
    simulation_id = str(uuid.uuid4())
    
    # Create initial simulation record
    active_simulations[simulation_id] = {
        "id": simulation_id,
        "status": "starting",
        "personaId": request.personaId,
        "webUrl": request.webUrl, 
        "task": request.task,
        "timestamp": datetime.now().isoformat(),
        "progress": 0
    }
    
    # Queue the simulation to run in background
    background_tasks.add_task(run_simulation, simulation_id, request)
    
    return {
        "success": True, 
        "simulationId": simulation_id,
        "message": "Simulation started"
    }

async def run_simulation(simulation_id: str, request: SimulationRequest):
    """Run a simulation in the background"""
    try:
        # Update status
        active_simulations[simulation_id]["status"] = "initializing"
        active_simulations[simulation_id]["progress"] = 10
        
        # Create persona object from the database or mock data
        # In a real implementation, you'd fetch this from your database
        persona = {
            "name": "Alex Johnson",
            "age": 35, 
            "gender": "Non-binary",
            "occupation": "Marketing Manager",
            "techExperience": "Intermediate",
            "traits": ["Analytical", "Detail-oriented", "Practical"],
            "goals": ["Find information quickly", "Make informed decisions", "Save time"],
            "painPoints": ["Complex interfaces", "Lack of clear information", "Slow websites"]
        }
        
        # Create memory stream
        memory_stream = MemoryStream()
        memory_streams[simulation_id] = memory_stream
        
        # Create browser connector
        browser_connector = UniversalBrowserConnector(headless=True)
        browser_connectors[simulation_id] = browser_connector
        
        # Update status
        active_simulations[simulation_id]["status"] = "creating_agent"
        active_simulations[simulation_id]["progress"] = 20
        
        # Create agent
        api_key = api_keys.get("openai", {}).get("key") if "openai" in api_keys else None
        agent = LLMAgent(
            memory_stream=memory_stream,
            browser_connector=browser_connector,
            api_key=api_key
        )
        
        # Set persona and intent
        agent.set_persona(persona)
        agent.set_intent(request.task)
        
        # Update status
        active_simulations[simulation_id]["status"] = "simulating"
        active_simulations[simulation_id]["progress"] = 30
        
        # Run the simulation
        max_cycles = request.maxCycles or 15
        session_result = agent.run_complete_session(
            url=request.webUrl,
            max_cycles=max_cycles
        )
        
        # Process results
        actions = []
        for memory in session_result['memories']:
            if memory['type'] == 'action_taken':
                actions.append({
                    "id": memory['id'],
                    "timestamp": memory['timestamp'],
                    "type": memory.get('metadata', {}).get('type', 'unknown'),
                    "target": memory.get('metadata', {}).get('name', ''),
                    "value": memory.get('metadata', {}).get('value', ''),
                    "reasoning": memory['content']
                })
        
        # Extract reflections and wonderings
        reflections = [memory['content'] for memory in session_result['memories'] 
                     if memory['type'] == 'reflection']
        wonderings = [memory['content'] for memory in session_result['memories'] 
                    if memory['type'] == 'wonder']
        
        # Save the result
        simulation_results[simulation_id] = {
            "id": simulation_id,
            "persona": persona,
            "webUrl": request.webUrl,
            "task": request.task,
            "taskCompleted": session_result['task_completed'],
            "durationSeconds": int(time.time() - active_simulations[simulation_id].get("start_time", time.time())),
            "actions": actions,
            "reflections": reflections or session_result.get('reflections', []),
            "wonderings": wonderings or session_result.get('wonderings', []),
            "timestamp": int(time.time() * 1000)
        }
        
        # Update status
        active_simulations[simulation_id]["status"] = "completed" 
        active_simulations[simulation_id]["progress"] = 100
        
        # Clean up resources
        if simulation_id in browser_connectors:
            browser_connectors[simulation_id].close()
            del browser_connectors[simulation_id]
            
    except Exception as e:
        # Update status to failed
        active_simulations[simulation_id]["status"] = "failed"
        active_simulations[simulation_id]["error"] = str(e)
        
        # Clean up resources in case of error
        if simulation_id in browser_connectors:
            try:
                browser_connectors[simulation_id].close()
            except:
                pass
            del browser_connectors[simulation_id]

@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get the status of a simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
        
    return active_simulations[simulation_id]

@app.get("/api/simulations/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Get the result of a completed simulation"""
    if simulation_id not in simulation_results:
        raise HTTPException(status_code=404, detail="Simulation result not found")
        
    return simulation_results[simulation_id]

@app.get("/api/simulations")
async def list_simulations(limit: int = 10, offset: int = 0):
    """List all simulations"""
    # Combine active and completed simulations
    all_simulations = []
    
    # Add active simulations
    for sim_id, sim in active_simulations.items():
        if sim_id in simulation_results:
            # This simulation is completed
            all_simulations.append(simulation_results[sim_id])
        else:
            # This simulation is still running
            all_simulations.append(sim)
    
    # Sort by timestamp (most recent first)
    all_simulations.sort(key=lambda s: s.get('timestamp', 0), reverse=True)
    
    # Apply pagination
    paginated = all_simulations[offset:offset+limit]
    
    return {
        "total": len(all_simulations),
        "simulations": paginated
    }

@app.post("/api/interview/{simulation_id}")
async def interview_agent(simulation_id: str, message: Dict[str, str]):
    """Interview the agent about their experience"""
    if "openai" not in api_keys:
        return {"success": False, "message": "OpenAI API key not configured"}
        
    if simulation_id not in simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    try:
        # Get the simulation result
        result = simulation_results[simulation_id]
        
        # Get the memory stream if available
        memories_text = ""
        if simulation_id in memory_streams:
            memories = memory_streams[simulation_id].get_all_memories()
            memories_text = "\n".join([
                f"[{memory['type']}] {memory['content']}" 
                for memory in memories[:50]  # Limit to most recent 50 memories
            ])
        else:
            # Use the saved results
            memories_text = (
                f"Task: {result['task']}\n" +
                "\n".join([f"[action] {action['reasoning']}" for action in result['actions']]) +
                "\n" + "\n".join([f"[reflection] {r}" for r in result['reflections']]) +
                "\n" + "\n".join([f"[wondering] {w}" for w in result['wonderings']])
            )
            
        # Create interview prompt
        prompt = f"""
You are an AI agent named {result['persona']['name']} with these characteristics:
- Age: {result['persona']['age']}
- Gender: {result['persona']['gender']}
- Occupation: {result['persona']['occupation']} 
- Tech Experience: {result['persona']['techExperience']}
- Traits: {', '.join(result['persona']['traits'])}
- Goals: {', '.join(result['persona']['goals'])}
- Pain Points: {', '.join(result['persona']['painPoints'])}

You have completed a web task: "{result['task']}" on {result['webUrl']}

Your memories from the session are:
{memories_text}

A UX researcher is now interviewing you. Respond naturally based on your persona and memories.

Researcher's question: "{message.get('text', '')}"

Respond as {result['persona']['name']} would, based on their characteristics and the web experience.
"""
        
        # Call the LLM for a response
        client = openai.Client(api_key=api_keys["openai"]["key"])
        response = client.chat.completions.create(
            model=api_keys["openai"].get("model", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return {
            "success": True,
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
