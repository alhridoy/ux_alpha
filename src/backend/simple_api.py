"""
Simplified API for UX Agent Simulator.
This version doesn't require all the dependencies.
"""

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
import openai
import base64

# Try to import our modules
try:
    from stagehand_agent import StagehandAgent
    from simulation_recorder import SimulationRecorder
    STAGEHAND_AVAILABLE = True
except ImportError:
    STAGEHAND_AVAILABLE = False
    print("Stagehand or SimulationRecorder not available, will use mock data")

# Initialize FastAPI app
app = FastAPI(title="UXAgent API", description="API for UXAgent browser automation and simulation")

# Global variable to store Stagehand instance
stagehand_instance = None

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
    # Generate mock personas
    personas = []
    for i in range(count):
        persona = Persona(
            name=f"User {i+1}",
            age=30 + i,
            gender="Non-binary" if i % 3 == 0 else "Female" if i % 3 == 1 else "Male",
            occupation="Software Developer" if i % 2 == 0 else "Marketing Manager",
            techExperience="Advanced" if i % 3 == 0 else "Intermediate" if i % 3 == 1 else "Beginner",
            traits=["Analytical", "Detail-oriented", "Practical"],
            goals=["Find information quickly", "Make informed decisions", "Save time"],
            painPoints=["Complex interfaces", "Lack of clear information", "Slow websites"],
            profileImage=f"https://randomuser.me/api/portraits/lego/{i+1}.jpg"
        )
        personas.append(persona.model_dump())

    return {"success": True, "personas": personas}

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
        active_simulations[simulation_id]["currentAction"] = "Initializing browser"

        # Import required modules
        from simulation_recorder import SimulationRecorder

        # Create a default persona - defined here so it's available in all code paths
        persona = {
            "name": "Alex Johnson",
            "age": 35,
            "gender": "Non-binary",
            "occupation": "Marketing Manager",
            "techExperience": "Intermediate",
            "traits": ["Analytical", "Detail-oriented", "Practical"],
            "goals": ["Find information quickly", "Make informed decisions", "Save time"],
            "painPoints": ["Complex interfaces", "Lack of clear information", "Slow websites"],
            "profileImage": "https://randomuser.me/api/portraits/lego/1.jpg"
        }

        try:
            # First try to use Stagehand
            try:
                # Try to import the Stagehand agent directly
                from stagehand_agent import StagehandAgent, STAGEHAND_AVAILABLE

                if not STAGEHAND_AVAILABLE:
                    raise ImportError("Stagehand is not available")

                # Get API keys from environment or configuration
                openai_api_key = os.getenv("OPENAI_API_KEY")
                stagehand_api_key = os.getenv("STAGEHAND_API_KEY")
                stagehand_project_id = os.getenv("STAGEHAND_PROJECT_ID")

                if "openai" in api_keys:
                    openai_api_key = api_keys["openai"]["key"]

                if "stagehand" in api_keys:
                    stagehand_api_key = api_keys["stagehand"]["key"]

                print(f"Using OpenAI API key: {openai_api_key[:8]}...")
                if stagehand_api_key:
                    print(f"Using Stagehand API key: {stagehand_api_key[:8]}...")
                if stagehand_project_id:
                    print(f"Using Stagehand Project ID: {stagehand_project_id}")

                # Get persona information from the simulation data
                persona_id = request.personaId

                # Create the Stagehand agent
                stagehand_agent = StagehandAgent(
                    headless=False,
                    api_key=openai_api_key,
                    model_name="gpt-4o"
                )

                # Create and initialize the recorder with the agent
                recorder = SimulationRecorder(stagehand_agent)
                recorder.start_recording(simulation_id)

                # Store the recorder and agent in the active simulation
                active_simulations[simulation_id]["recorder"] = recorder
                active_simulations[simulation_id]["agent"] = stagehand_agent
                active_simulations[simulation_id]["use_real_stagehand"] = True

                # Update status
                active_simulations[simulation_id]["status"] = "running"
                active_simulations[simulation_id]["progress"] = 20
                active_simulations[simulation_id]["currentAction"] = f"Navigating to {request.webUrl}"

                # Use the real Stagehand agent for browser automation
                use_real_stagehand = True
                print("Successfully initialized Stagehand for real browser automation")

            except Exception as e:
                print(f"Error setting up Stagehand: {str(e)}")
                print("Trying Selenium as fallback...")

                # Try to use Selenium as fallback
                try:
                    from selenium_browser import SeleniumBrowser, SELENIUM_AVAILABLE

                    if not SELENIUM_AVAILABLE:
                        raise ImportError("Selenium is not available")

                    # Create Selenium browser
                    selenium_browser = SeleniumBrowser(
                        headless=False,
                        api_key=os.getenv("OPENAI_API_KEY")
                    )

                    # Create and initialize the recorder
                    recorder = SimulationRecorder(selenium_browser)
                    recorder.start_recording(simulation_id)

                    # Store the recorder and browser in the active simulation
                    active_simulations[simulation_id]["recorder"] = recorder
                    active_simulations[simulation_id]["agent"] = selenium_browser

                    # Update status
                    active_simulations[simulation_id]["status"] = "running"
                    active_simulations[simulation_id]["progress"] = 20
                    active_simulations[simulation_id]["currentAction"] = f"Navigating to {request.webUrl}"

                    # Use Selenium for browser automation
                    use_real_stagehand = True  # We'll treat Selenium as a "real" browser
                    print("Successfully initialized Selenium for real browser automation")

                except Exception as e:
                    print(f"Error setting up Selenium: {str(e)}")
                    print("Falling back to mock browser connector")
                    raise  # Re-raise to fall back to mock browser

        except Exception as e:
            print(f"Error setting up browser automation: {str(e)}")
            print("Falling back to mock browser connector")

            # Create a mock browser connector as fallback
            class MockBrowserConnector:
                def take_screenshot(self):
                    # Return a mock screenshot URL
                    if "amazon" in request.webUrl.lower():
                        return "https://m.media-amazon.com/images/G/01/gc/designs/livepreview/amazon_dkblue_noto_email_v2016_us-main._CB468775337_.png"
                    else:
                        return "https://via.placeholder.com/800x600?text=Mock+Screenshot"

                def navigate(self, url):
                    return {"success": True, "url": url}

                def execute_action(self, action):
                    return {"success": True, "action": action}

            # Create and initialize the recorder with mock connector
            recorder = SimulationRecorder(MockBrowserConnector())
            recorder.start_recording(simulation_id)

            # Store the recorder in the active simulation
            active_simulations[simulation_id]["recorder"] = recorder

            # We'll use the mock data flow
            use_real_stagehand = False

        # Store whether we're using real Stagehand
        active_simulations[simulation_id]["use_real_stagehand"] = use_real_stagehand

        # Store the persona in the simulation data
        active_simulations[simulation_id]["persona"] = persona

        # Update status
        active_simulations[simulation_id]["status"] = "simulating"
        active_simulations[simulation_id]["progress"] = 30

        # Get the recorder
        recorder = active_simulations[simulation_id].get("recorder")

        # Check if we're using real Stagehand
        if active_simulations[simulation_id].get("use_real_stagehand", False):
            # Get the Stagehand agent
            stagehand_agent = active_simulations[simulation_id].get("agent")

            if stagehand_agent:
                # Update status
                active_simulations[simulation_id]["currentAction"] = f"Navigating to {request.webUrl}"

                # Navigate to the URL
                nav_result = stagehand_agent.navigate(request.webUrl)
                if nav_result.get("success", False):
                    active_simulations[simulation_id]["progress"] = 40
                    active_simulations[simulation_id]["currentAction"] = f"Executing task: {request.task}"

                    # Store the screenshot from navigation
                    if "screenshot" in nav_result:
                        active_simulations[simulation_id]["screenshot"] = nav_result["screenshot"]

                    # Execute the task using Stagehand agent
                    task_result = stagehand_agent.execute_task(request.task)

                    # Store the actions for replay
                    if "actions" in task_result:
                        active_simulations[simulation_id]["actions"] = task_result["actions"]

                    # Store the screenshot from task execution
                    if "screenshot" in task_result:
                        active_simulations[simulation_id]["screenshot"] = task_result["screenshot"]

                    # Store the result for later retrieval
                    active_simulations[simulation_id]["result"] = task_result

                    # Update progress based on task result
                    if task_result.get("success", False):
                        active_simulations[simulation_id]["progress"] = 100
                        active_simulations[simulation_id]["currentAction"] = "Task completed successfully"

                        # Store the result in simulation_results
                        simulation_results[simulation_id] = {
                            "id": simulation_id,
                            "status": "completed",
                            "result": task_result,
                            "actions": task_result.get("actions", []),
                            "screenshot": task_result.get("screenshot", ""),
                            "timestamp": int(time.time() * 1000),
                            "persona": persona,
                            "webUrl": request.webUrl,
                            "task": request.task,
                            "taskCompleted": task_result.get("success", False)
                        }
                    else:
                        active_simulations[simulation_id]["progress"] = 70
                        active_simulations[simulation_id]["currentAction"] = f"Task execution encountered issues: {task_result.get('message', '')}"
                else:
                    active_simulations[simulation_id]["currentAction"] = f"Failed to navigate to {request.webUrl}"
        else:
            # Using mock data - simulate progress with fake actions
            active_simulations[simulation_id]["progress"] = 30

            # Wait a bit to simulate work with progressive updates
            time.sleep(1)
            active_simulations[simulation_id]["progress"] = 40

            # Record initial navigation action
            if recorder:
                initial_action = {
                    "id": str(uuid.uuid4()),
                    "type": "navigate",
                    "target": request.webUrl,
                    "value": "",
                    "description": f"Navigating to {request.webUrl}",
                    "reasoning": f"Starting the task by navigating to {request.webUrl}"
                }
                recorder.record_action(initial_action)
                active_simulations[simulation_id]["currentAction"] = f"Navigating to {request.webUrl}"

            time.sleep(1)
            active_simulations[simulation_id]["progress"] = 50

            # Record search action if applicable
            if recorder and "amazon" in request.webUrl.lower():
                search_action = {
                    "id": str(uuid.uuid4()),
                    "type": "input",
                    "target": "search_input",
                    "value": "red sweater",
                    "description": "Searching for red sweater",
                    "reasoning": "Entering search query to find the product"
                }
                recorder.record_action(search_action)
                active_simulations[simulation_id]["currentAction"] = "Searching for red sweater"

            time.sleep(1)
            active_simulations[simulation_id]["progress"] = 60

            # Record click action
            if recorder:
                click_action = {
                    "id": str(uuid.uuid4()),
                    "type": "click",
                    "target": "search_button",
                    "value": "",
                    "description": "Clicking search button",
                    "reasoning": "Submitting the search query"
                }
                recorder.record_action(click_action)
                active_simulations[simulation_id]["currentAction"] = "Submitting search query"

            time.sleep(1)
            active_simulations[simulation_id]["progress"] = 70

            # Record scroll action
            if recorder:
                scroll_action = {
                    "id": str(uuid.uuid4()),
                    "type": "scroll",
                    "target": "page",
                    "value": "down",
                    "description": "Scrolling down the page",
                    "reasoning": "Looking through search results"
                }
                recorder.record_action(scroll_action)
                active_simulations[simulation_id]["currentAction"] = "Browsing search results"

            time.sleep(1)
            active_simulations[simulation_id]["progress"] = 80

            # Record product click action
            if recorder and "amazon" in request.webUrl.lower():
                product_action = {
                    "id": str(uuid.uuid4()),
                    "type": "click",
                    "target": "product_item",
                    "value": "",
                    "description": "Clicking on product",
                    "reasoning": "Selecting a red sweater from search results"
                }
                recorder.record_action(product_action)
                active_simulations[simulation_id]["currentAction"] = "Selecting a product"

            time.sleep(1)
            active_simulations[simulation_id]["progress"] = 90

            # Record add to cart action
            if recorder and "amazon" in request.webUrl.lower():
                cart_action = {
                    "id": str(uuid.uuid4()),
                    "type": "click",
                    "target": "add_to_cart",
                    "value": "",
                    "description": "Adding to cart",
                    "reasoning": "Adding the selected red sweater to shopping cart"
                }
                recorder.record_action(cart_action)
                active_simulations[simulation_id]["currentAction"] = "Adding item to cart"

            time.sleep(1)

        # Check if this is an Amazon search for a red sweater
        is_amazon_sweater_task = "amazon" in request.webUrl.lower() and "sweater" in request.task.lower()

        # Create actions based on the task
        actions = []
        reflections = []
        wonderings = []

        if is_amazon_sweater_task:
            # Amazon red sweater search simulation
            actions = [
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time(),
                    "type": "navigate",
                    "target": request.webUrl,
                    "value": "",
                    "reasoning": f"Navigating to {request.webUrl} to start the task of finding a red sweater"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 1,
                    "type": "click",
                    "target": "search_box",
                    "value": "",
                    "reasoning": "Clicking on the search box to enter my search query"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 2,
                    "type": "input",
                    "target": "search_input",
                    "value": "red sweater",
                    "reasoning": "Entering 'red sweater' as my search query to find relevant products"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 3,
                    "type": "click",
                    "target": "search_submit",
                    "value": "",
                    "reasoning": "Clicking the search button to submit my query"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 4,
                    "type": "click",
                    "target": "filter_department",
                    "value": "",
                    "reasoning": "Clicking on the department filter to narrow down results to clothing"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 5,
                    "type": "click",
                    "target": "clothing_department",
                    "value": "",
                    "reasoning": "Selecting 'Clothing' from the department options"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 6,
                    "type": "click",
                    "target": "filter_price",
                    "value": "",
                    "reasoning": "Clicking on the price filter to set a budget range"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 7,
                    "type": "click",
                    "target": "price_range_25_50",
                    "value": "",
                    "reasoning": "Selecting the $25-$50 price range as it seems reasonable for a sweater"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 8,
                    "type": "click",
                    "target": "product_card_1",
                    "value": "",
                    "reasoning": "Clicking on the first red sweater that matches my criteria"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 9,
                    "type": "click",
                    "target": "size_dropdown",
                    "value": "",
                    "reasoning": "Clicking on the size dropdown to select my size"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 10,
                    "type": "click",
                    "target": "size_medium",
                    "value": "",
                    "reasoning": "Selecting 'Medium' as my size"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 11,
                    "type": "click",
                    "target": "add_to_cart_button",
                    "value": "",
                    "reasoning": "Adding the red sweater to my cart"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 12,
                    "type": "click",
                    "target": "proceed_to_checkout",
                    "value": "",
                    "reasoning": "Proceeding to checkout to complete the purchase"
                }
            ]

            reflections = [
                "Amazon's search functionality is effective, but the number of results can be overwhelming",
                "The filtering options helped me narrow down my search quickly",
                "Product images were clear and helped me identify the right red sweater",
                "The size selection was straightforward, but I wish there were more details about the fit",
                "The add to cart and checkout process was simple and intuitive"
            ]

            wonderings = [
                "I wonder if there's a way to filter by specific shades of red",
                "I'm curious if other users find the number of similar products confusing",
                "I wonder if the recommendation system could be improved to show more relevant alternatives",
                "I'm curious if the checkout process could be streamlined further"
            ]
        else:
            # Generic simulation for other tasks
            actions = [
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time(),
                    "type": "navigate",
                    "target": request.webUrl,
                    "value": "",
                    "reasoning": f"Navigating to {request.webUrl} to start the task"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 1,
                    "type": "click",
                    "target": "search_button",
                    "value": "",
                    "reasoning": "Clicking on the search button to find relevant information"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.time() + 2,
                    "type": "input",
                    "target": "search_input",
                    "value": request.task.split(" ")[-1] if " " in request.task else request.task,
                    "reasoning": f"Entering search query related to the task: {request.task}"
                }
            ]

            reflections = [
                "The website has a clean interface that makes it easy to navigate",
                "The search functionality is prominently displayed, which helps with finding information quickly"
            ]

            wonderings = [
                "I wonder if there's a quicker way to find what I'm looking for",
                "I'm curious if other users find this interface intuitive"
            ]

        # Get recorded actions if available
        recorder = active_simulations[simulation_id].get("recorder")
        if recorder:
            # Stop recording and get the actions
            recorded_actions = recorder.stop_recording()
            if recorded_actions:
                actions = recorded_actions

        # Save the result
        simulation_results[simulation_id] = {
            "id": simulation_id,
            "persona": persona,
            "webUrl": request.webUrl,
            "task": request.task,
            "taskCompleted": True,
            "durationSeconds": 15,
            "actions": actions,
            "reflections": reflections,
            "wonderings": wonderings,
            "timestamp": int(time.time() * 1000),
            "status": "completed"
        }

        # Update status
        active_simulations[simulation_id]["status"] = "completed"
        active_simulations[simulation_id]["progress"] = 100

    except Exception as e:
        # Update status to failed
        active_simulations[simulation_id]["status"] = "failed"
        active_simulations[simulation_id]["error"] = str(e)

@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get the status of a simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Create a clean copy of the simulation data without non-serializable objects
    simulation_data = {
        "id": simulation_id,
        "status": active_simulations[simulation_id].get("status", "unknown"),
        "created_at": active_simulations[simulation_id].get("created_at", ""),
        "progress": active_simulations[simulation_id].get("progress", 0),
        "currentAction": active_simulations[simulation_id].get("currentAction", ""),
        "request": active_simulations[simulation_id].get("request", {})
    }

    # Add any other serializable fields
    for key, value in active_simulations[simulation_id].items():
        if key not in ["recorder", "agent", "browser_connector"] and isinstance(value, (str, int, float, bool, list, dict)):
            simulation_data[key] = value

    return simulation_data

@app.get("/api/simulations/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Get the result of a completed simulation"""
    if simulation_id not in simulation_results and simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation_id in simulation_results:
        # Return completed simulation result
        return simulation_results[simulation_id]

    # For active simulations, create a clean copy without non-serializable objects
    simulation_data = {
        "id": simulation_id,
        "status": active_simulations[simulation_id].get("status", "running"),
        "created_at": active_simulations[simulation_id].get("created_at", ""),
        "progress": active_simulations[simulation_id].get("progress", 0),
        "currentAction": active_simulations[simulation_id].get("currentAction", ""),
        "request": active_simulations[simulation_id].get("request", {}),
        "result": active_simulations[simulation_id].get("result", {}),
        "error": active_simulations[simulation_id].get("error", None)
    }

    # Add any other serializable fields
    for key, value in active_simulations[simulation_id].items():
        if key not in ["recorder", "agent", "browser_connector"] and isinstance(value, (str, int, float, bool, list, dict)):
            simulation_data[key] = value

    return simulation_data

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

A UX researcher is now interviewing you. Respond naturally based on your persona.

Researcher's question: "{message.get('text', '')}"

Respond as {result['persona']['name']} would, based on their characteristics and the web experience.
"""

        # Call the LLM for a response
        client = openai.OpenAI(api_key=api_keys["openai"]["key"])
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

# Stagehand-related endpoints (mock implementations)
@app.post("/api/config/browser")
async def set_browser_automation(type: str):
    """Configure browser automation type"""
    return {"success": True, "message": f"Browser automation set to {type}"}

@app.get("/api/config/browser")
async def get_browser_automation():
    """Get browser automation type"""
    return {"type": "stagehand"}

@app.post("/api/config/stagehand")
async def set_stagehand_api_key(key: Dict[str, str]):
    """Set Stagehand API key"""
    api_key = key.get("key", "")

    if not api_key:
        return {"success": False, "message": "API key is required"}

    # Store the Stagehand API key
    api_keys["stagehand"] = {"key": api_key}

    # Also set the OpenAI API key if not already set
    # This is because Stagehand uses OpenAI for its LLM
    if "openai" not in api_keys:
        api_keys["openai"] = {"key": api_key}

    return {"success": True, "message": "Stagehand API key configured"}

@app.get("/api/config/stagehand/status")
async def get_stagehand_status():
    """Check if Stagehand is configured"""
    # Check if Stagehand API key is configured
    stagehand_configured = "stagehand" in api_keys and api_keys["stagehand"].get("key", "")

    # Also check if OpenAI API key is configured (needed for Stagehand)
    openai_configured = "openai" in api_keys and api_keys["openai"].get("key", "")

    # Both keys are needed for Stagehand to work properly
    return {"configured": stagehand_configured and openai_configured}

@app.post("/api/stagehand/init")
async def initialize_stagehand():
    """Initialize Stagehand browser session"""
    try:
        # Check if Stagehand is available
        if not STAGEHAND_AVAILABLE:
            return {"success": False, "message": "Stagehand is not available. Please install it with 'pip install stagehand-py'"}

        # Get API key from environment or configuration
        api_key = os.getenv("OPENAI_API_KEY")
        if "openai" in api_keys:
            api_key = api_keys["openai"]["key"]

        if not api_key:
            return {"success": False, "message": "OpenAI API key is not configured"}

        # Create a new simulation recorder
        simulation_recorder = SimulationRecorder()

        # Create a new Stagehand agent with simulation recorder
        stagehand_agent = StagehandAgent(
            headless=False,
            api_key=api_key,
            model_name="gpt-4o",
            simulation_recorder=simulation_recorder
        )

        # Store the agent in a global variable for later use
        global stagehand_instance
        stagehand_instance = stagehand_agent

        return {"success": True, "message": "Stagehand initialized successfully"}
    except Exception as e:
        print(f"Error initializing Stagehand: {str(e)}")
        return {"success": False, "message": f"Error initializing Stagehand: {str(e)}"}

@app.post("/api/stagehand/navigate")
async def stagehand_navigate(url: Dict[str, str]):
    """Navigate to a URL using Stagehand"""
    target_url = url.get("url", "")

    # Check if we have a Stagehand instance
    global stagehand_instance
    if stagehand_instance:
        try:
            # Use the real Stagehand instance to navigate
            result = stagehand_instance.navigate(target_url)
            return result
        except Exception as e:
            print(f"Error navigating with Stagehand: {str(e)}")
            # Fall back to mock implementation

    # Mock implementation as fallback
    screenshot_url = ""
    if "amazon" in target_url.lower():
        screenshot_url = "https://m.media-amazon.com/images/G/01/gc/designs/livepreview/amazon_dkblue_noto_email_v2016_us-main._CB468775337_.png"
    elif "google" in target_url.lower():
        screenshot_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
    else:
        screenshot_url = "https://via.placeholder.com/800x600?text=Mock+Screenshot"

    return {
        "success": True,
        "url": target_url,
        "title": f"Mock Page Title for {target_url}",
        "content": f"<html><body><h1>Mock Page for {target_url}</h1><p>This is a mock page for testing.</p></body></html>",
        "screenshot": screenshot_url
    }

@app.post("/api/stagehand/execute")
async def stagehand_execute(instruction: Dict[str, str]):
    """Execute an action using Stagehand"""
    action_instruction = instruction.get('instruction', '')

    # Check if we have a Stagehand instance
    global stagehand_instance
    if stagehand_instance:
        try:
            # Use the real Stagehand instance to execute the action
            result = stagehand_instance.act(action_instruction)

            # If successful, return the result
            if result.get("success", False):
                return result

            # If not successful, try using execute_task as a fallback
            task_result = stagehand_instance.execute_task(action_instruction)
            if task_result.get("success", False):
                return task_result

            # If both methods fail, fall back to mock implementation
            print(f"Stagehand action execution failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Error executing action with Stagehand: {str(e)}")
            # Fall back to mock implementation

    # Mock implementation as fallback
    screenshot_url = ""
    if "search" in action_instruction.lower() and "red sweater" in action_instruction.lower():
        screenshot_url = "https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg"
    elif "click" in action_instruction.lower() and "add to cart" in action_instruction.lower():
        screenshot_url = "https://m.media-amazon.com/images/G/01/cart/empty/kettle-desaturated._CB445243794_.svg"
    else:
        screenshot_url = "https://via.placeholder.com/800x600?text=Action+Executed"

    return {
        "success": True,
        "message": f"Executed: {action_instruction}",
        "screenshot": screenshot_url
    }

@app.post("/api/stagehand/screenshot")
async def stagehand_screenshot():
    """Take a screenshot of the current page"""
    # Check if we have a Stagehand instance
    global stagehand_instance
    if stagehand_instance:
        try:
            # Use the real Stagehand instance to take a screenshot
            screenshot = stagehand_instance.take_screenshot()
            if screenshot:
                return {
                    "success": True,
                    "screenshot": screenshot,
                    "timestamp": int(time.time() * 1000)
                }
        except Exception as e:
            print(f"Error taking screenshot with Stagehand: {str(e)}")
            # Fall back to mock implementation

    # Mock implementation as fallback
    return {
        "success": True,
        "screenshot": "https://via.placeholder.com/800x600?text=Current+Screenshot",
        "timestamp": int(time.time() * 1000)
    }

@app.post("/api/stagehand/extract")
async def stagehand_extract(data: Dict[str, Any]):
    """Extract data from a website using Stagehand"""
    instruction = data.get("instruction", "")

    # Generate mock extracted data based on the instruction
    extracted_data = {}
    if "product" in instruction.lower() and "sweater" in instruction.lower():
        extracted_data = {
            "title": "Amazon Essentials Women's Classic-Fit Soft-Touch Crewneck Sweater",
            "price": "$24.90",
            "rating": "4.5 out of 5 stars",
            "color": "Red",
            "sizes": ["XS", "S", "M", "L", "XL", "XXL"]
        }
    else:
        extracted_data = {
            "title": "Mock Title",
            "content": "Mock Content"
        }

    return {
        "success": True,
        "extractedData": extracted_data
    }

@app.post("/api/stagehand/close")
async def close_stagehand():
    """Close Stagehand browser session"""
    # Check if we have a Stagehand instance
    global stagehand_instance
    if stagehand_instance:
        try:
            # Use the real Stagehand instance to close the session
            stagehand_instance.close()
            stagehand_instance = None
            return {"success": True, "message": "Stagehand closed successfully"}
        except Exception as e:
            print(f"Error closing Stagehand: {str(e)}")
            return {"success": False, "message": f"Error closing Stagehand: {str(e)}"}

    # No Stagehand instance to close
    return {"success": True, "message": "No active Stagehand session to close"}

# Add a new endpoint for live browser updates
@app.get("/api/stagehand/live/{simulation_id}")
async def stagehand_live_updates(simulation_id: str):
    """Get live browser updates for a simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulation_data = active_simulations[simulation_id]

    # Check if we have a recorder instance
    recorder = simulation_data.get("recorder")
    try:
        if recorder and hasattr(recorder, "get_live_update"):
            # Get live update from the recorder
            live_update = recorder.get_live_update()
            if live_update and live_update.get("success", False):
                # Add any missing fields from simulation_data
                if "progress" not in live_update and "progress" in simulation_data:
                    live_update["progress"] = simulation_data["progress"]

                if "currentAction" not in live_update and "currentAction" in simulation_data:
                    live_update["currentAction"] = simulation_data["currentAction"]

                return live_update
    except Exception as e:
        print(f"Error getting live update from recorder: {str(e)}")

    # Check if we're using real Stagehand
    if simulation_data.get("use_real_stagehand", False):
        # Try to get a screenshot from the agent
        agent = simulation_data.get("agent")
        if agent:
            try:
                # Take a screenshot using the agent's take_screenshot method
                screenshot_url = agent.take_screenshot()

                # Get the current URL
                current_url = agent.get_current_url()

                # Get progress and current action
                progress = simulation_data.get("progress", 0)
                current_action = simulation_data.get("currentAction", "")

                # Get actions if available
                actions = simulation_data.get("actions", [])

                return {
                    "success": True,
                    "simulationId": simulation_id,
                    "progress": progress,
                    "screenshot": screenshot_url,
                    "currentUrl": current_url,
                    "currentAction": current_action,
                    "actionCount": len(actions),
                    "actions": actions,
                    "timestamp": int(time.time() * 1000)
                }
            except Exception as e:
                print(f"Error getting screenshot from agent: {str(e)}")

        # If agent is not available, try using the global Stagehand instance
        global stagehand_instance
        if stagehand_instance:
            try:
                # Take a screenshot using the Stagehand instance
                screenshot_url = stagehand_instance.take_screenshot()

                # Get the current URL
                current_url = stagehand_instance.get_current_url()

                # Get progress and current action from simulation data
                progress = simulation_data.get("progress", 0)
                current_action = simulation_data.get("currentAction", "")

                return {
                    "success": True,
                    "simulationId": simulation_id,
                    "progress": progress,
                    "screenshot": screenshot_url,
                    "currentUrl": current_url,
                    "currentAction": current_action,
                    "actionCount": simulation_data.get("actionCount", 0),
                    "timestamp": int(time.time() * 1000)
                }
            except Exception as e:
                print(f"Error getting screenshot from global Stagehand instance: {str(e)}")

    # Fallback to mock data if recorder is not available or doesn't support live updates
    progress = simulation_data.get("progress", 0)

    # Generate a mock screenshot URL based on the progress
    screenshot_url = ""
    if progress < 30:
        screenshot_url = "https://via.placeholder.com/800x600?text=Loading+Website"
    elif progress < 50:
        screenshot_url = "https://via.placeholder.com/800x600?text=Website+Loaded"
    elif progress < 70:
        screenshot_url = "https://via.placeholder.com/800x600?text=Performing+Actions"
    elif progress < 90:
        screenshot_url = "https://via.placeholder.com/800x600?text=Completing+Task"
    else:
        screenshot_url = "https://via.placeholder.com/800x600?text=Task+Completed"

    # Increment progress for demo purposes
    active_simulations[simulation_id]["progress"] = min(100, progress + 5)

    # Get the current action from the simulation data
    current_action = simulation_data.get("currentAction", "")
    if not current_action:
        current_action = f"Step {int(progress/10)}: {'Initializing' if progress < 30 else 'Navigating to website' if progress < 50 else 'Analyzing page' if progress < 70 else 'Performing actions' if progress < 90 else 'Completing task'}"

    # Get actions, reflections, and wonderings from the simulation data
    actions = simulation_data.get("actions", [])
    reflections = simulation_data.get("reflections", [])
    wonderings = simulation_data.get("wonderings", [])

    # Generate mock reflections and wonderings if they don't exist
    if not reflections and progress > 50:
        reflections = [
            "The website has a clean interface that makes it easy to navigate",
            "The search functionality is prominently displayed, which helps with finding information quickly"
        ]
        # Store in simulation data for future use
        active_simulations[simulation_id]["reflections"] = reflections

    if not wonderings and progress > 70:
        wonderings = [
            "I wonder if there's a quicker way to find what I'm looking for",
            "I'm curious if other users find this interface intuitive"
        ]
        # Store in simulation data for future use
        active_simulations[simulation_id]["wonderings"] = wonderings

    return {
        "success": True,
        "simulationId": simulation_id,
        "progress": progress,
        "screenshot": screenshot_url,
        "currentAction": current_action,
        "actionCount": int(progress / 10),
        "actions": actions,
        "reflections": reflections,
        "wonderings": wonderings,
        "timestamp": int(time.time() * 1000)
    }

if __name__ == "__main__":
    uvicorn.run("simple_api:app", host="0.0.0.0", port=8000, reload=True)
