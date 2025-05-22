I. High-Level Architecture & Core Technologies
Programming Language: Python is the natural choice due to its strong ecosystem for web automation (Selenium), NLP (Hugging Face Transformers, spaCy), and LLM SDKs (OpenAI, Anthropic, Langchain).
LLM API: You'll need access to one or more powerful LLMs.
OpenAI API (GPT-3.5-turbo, GPT-4, GPT-4o): Good for reasoning, generation, and following complex instructions.
Anthropic Claude API (Claude 3 Sonnet/Opus): Strong reasoning, handles long context well.
Open Source Models (Llama 3, Mixtral): If you want more control or to run locally (requires significant hardware for good performance). You'd use libraries like Hugging Face transformers.
Web Interaction: Selenium for browser control (as mentioned in the paper).
HTML Parsing: BeautifulSoup4 for parsing and simplifying HTML.
Vector Embeddings & Similarity:
Sentence-Transformers (e.g., all-MiniLM-L6-v2) for generating embeddings.
ScaPy, Faiss, or even simple NumPy/SciPy for cosine similarity.
II. Building the Memory Stream
The Memory Stream is central. It stores diverse memory "pieces."
Memory Piece Structure:
Each memory piece should be an object or dictionary containing at least:
id: Unique identifier.
type: Enum/string (e.g., "observation", "action_taken", "plan_step", "reflection", "wonder", "persona_detail", "intent").
content: The natural language description of the memory (e.g., "Observed a search box input field", "Clicked on 'Add to Cart' button", "Reflected that I prefer eco-friendly products").
timestamp: When the memory was created.
source_module: Which module generated this memory (e.g., "PerceptionModule", "ActionModule", "ReflectionModule").
embedding: (Optional, can be computed on-demand or stored) The vector embedding of the content.
importance_score: (Optional, can be computed on-demand or stored) Numeric score.
Storage:
In-Session: For a single simulation run, a Python list of these memory objects is sufficient.
Persistence (Optional): If you need to analyze across sessions or resume, consider:
JSON files (one per agent/session).
A NoSQL database like MongoDB (good for flexible schemas).
A vector database (Pinecone, Weaviate) if retrieval performance at scale becomes critical.
Retrieval Mechanism:
This is crucial for feeding relevant context to the LLM modules.
Function retrieve_memories(query_text, current_time, num_memories_to_retrieve, weights):
query_text: What the current module is thinking about (e.g., "What should I do next?", "What products did I see?").
weights: A dictionary like {'importance': 0.3, 'relevance': 0.4, 'recency': 0.3, 'type_weights': {...}} to adjust scoring.
Calculating Scores for each memory piece:
Importance Score:
When a memory is created (especially observations by Perception, reflections by Reflection), you can have an LLM assign an importance score.
Prompt (example for Perception): "Given the agent's intent: '[Agent Intent]' and persona: '[Agent Persona]', rate the importance of the following observation for achieving the intent on a scale of 1-10: '[Observation Content]'. Output only the number."
Store this score or compute on-demand if too slow during generation.
Relevance Score:
Generate an embedding for query_text using your chosen embedding model.
For each memory in the Memory Stream, get its pre-computed embedding (or compute it).
Calculate cosine similarity between the query_text embedding and each memory's embedding. This is the relevance score.
Recency Score:
Use the formula: recency = 1 / exp(k * (current_time - memory_timestamp)).
k=1 is given as a starting point. current_time and memory_timestamp should be numerical (e.g., seconds since start of simulation).
Type Weight (w_type):
The paper mentions "Each module uses separate parameter sets to align with their distinct retrieval priorities".
This means the weights dictionary passed to retrieve_memories might have a sub-dictionary like type_weights: {"observation": 1.2, "reflection": 1.5, "action_taken": 0.8}.
This w_type factor can be applied to the final score of memories of a certain type.
Combined Score:
final_score = (importance_score * w_imp + relevance_score * w_rel + recency_score * w_rec) * w_type
Normalize scores (e.g., to 0-1 range) before combining if they are on different scales.
Selection: Sort memories by final_score and return the top num_memories_to_retrieve.
III. Building the LLM Agent Modules (Two-Loop Architecture)
This involves a lot of prompt engineering and orchestrating LLM calls.
Universal Browser Connector (Simplified Interface for LLM):
HTML Simplifier:
Input: Raw HTML (from Selenium: driver.page_source).
Use BeautifulSoup to parse.
Implement the "recipe-based" parsing:
Define which tags are important (e.g., <a>, <button>, <input>, <div> with specific classes).
Extract text content (handle text_selector, text_js potentially by running JS via Selenium if needed, though text_js is complex).
Extract key attributes (href, role, value, placeholder, custom name you assign).
The paper's hierarchical naming (product.add_to_cart) is crucial. You'll need logic to traverse parent elements to construct these names.
Output: The simplified JSON structure ({url, page, clickables, inputs, error_message}).
Action Executor:
Input: An action from the Action Module (e.g., {type: "click", name: "product.add_to_cart"}).
Translate this into Selenium commands:
Find the element using the hierarchical name (you might need to map this to XPath or a unique CSS selector you generated during simplification).
Execute: element.click(), element.send_keys(), driver.back(), etc.
Fast Loop Modules:
Perception Module:
Input: Simplified HTML from Universal Browser Connector.
LLM Call:
Prompt (see Appendix A.2): "You are the PERCEIVE module... Read the given viewpoint... list all observations... Output as a JSON object: {'observations': ['<obs1>', '<obs2>']}"
Feed the simplified HTML as context.
Output: List of observation strings.
Action: Create "observation" memory pieces and add them to Memory Stream (potentially calculate importance).
Planning Module (System 1 - Fast):
Input: Agent's persona, intent, k most relevant memories (retrieved using a query like "Current situation and goals").
LLM Call:
Prompt (see Appendix A.3): "You are tasked with creating/updating a detailed plan... Persona: [...], Intent: [...], Relevant Memories: [...], Previous Plan (if any): [...]. Output JSON: {'rationale': '...', 'plan': 'step1\nstep2...', 'next_step': 'current step to execute'}"
Output: Rationale, new/updated plan (string with steps), next step string.
Action: Create/update "plan_step" memory pieces.
Action Module:
Input: Current environment state (simplified HTML again, especially clickables and inputs), persona, intent, the next_step from Planning Module, k relevant memories.
LLM Call:
Prompt (see Appendix A.4): "You are the Action Module. Persona: [...], Intent: [...], Current Plan Step: '[next_step]', Environment: {'clickables': [...], 'inputs': [...]}. Translate the plan step into specific actions. Output JSON: {'actions': [{'type': 'click', 'name': '...', 'description': '...'}]}"
Output: A list of action objects (e.g., [{type: "click", name: "search_button", description: "Clicking search button"}]). Usually one action, but the paper implies an array.
Action:
Create "action_taken" memory pieces.
Send the action(s) to the Universal Browser Connector for execution.
Slow Loop Modules (Can run asynchronously/periodically):
Reflection Module:
Input: k recent memories (e.g., last N observations, actions, plan updates). Persona.
LLM Call:
Prompt (see Appendix A.5): "You are a human viewing a web page... Based on recent memories: [...] and persona: [...], what are your high-level insights or reflections? Output JSON: {'insights': ['<insight1>', '<insight2>']}"
Output: List of reflection strings.
Action: Create "reflection" memory pieces.
Wonder Module:
Input: Persona, k recent memories.
LLM Call:
Prompt (see Appendix A.6): "You are tasked with 'wondering'... Persona: [...], Recent Memories: [...]. Generate 0 to 3 random thoughts. Output JSON: {'thoughts': ['<thought1>']}"
Output: List of wonder strings.
Action: Create "wonder" memory pieces.
Orchestration:
The main loop would likely iterate: Perception -> Planning -> Action.
The Slow Loop modules could run in separate threads/processes, triggered after a certain number of Fast Loop iterations or after a certain amount of time.
All modules read from and write to the shared Memory Stream.
IV. Persona Generator Module
Input: Example persona string, demographic constraints (age, gender, income range).
LLM Call:
Prompt (see Appendix A.1): "Generate a persona... Age: {age}, Gender: {gender}, Income: {income_range}... Different from previous personas: [list or example]. Output only the persona text."
Output: Persona string.
V. Data Collection & Interfaces
Action Trace: Log every action object produced by the Action Module.
Reasoning Trace: This is essentially the entire Memory Stream for a session.
Simulation Replay Interface:
Load an Action Trace.
Use Selenium to navigate to the initial URL.
For each action in the trace:
Execute the action using Selenium.
Highlight the target element (Selenium can do this with JavaScript execution).
Pause or allow step-through.
Agent Interview Interface:
A simple chat UI.
When a UX researcher sends a message:
Load the agent's Memory Stream for the relevant session.
Use the researcher's message and the Memory Stream as context for an LLM.
Prompt: "You are an AI agent named [Agent Persona Name]. You have completed a web task. A UX researcher is now interviewing you. Your memories from the session are: [Formatted Memory Stream]. Researcher's question: '[Researcher's Message]'. Respond naturally based on your persona and memories."
Display the LLM's response.
Handle image uploads by passing image descriptions/URLs to the LLM if it's multimodal, or just acknowledging the upload.
VI. Key Challenges & Considerations
Prompt Engineering: This is 80% of the work. Each module's LLM call needs carefully crafted prompts to ensure reliable and correct output.
Latency: Multiple LLM calls per step can be slow. Consider:
Using faster models (e.g., GPT-3.5-turbo) for less critical steps.
Batching LLM calls if possible (unlikely for sequential agent steps).
Optimizing retrieval.
Cost: LLM API calls can get expensive, especially with GPT-4/Claude Opus for every step.
Robustness of HTML Parsing: Real-world websites are messy. The "recipe" for the Universal Browser Connector needs to be quite robust or adaptable. Dynamic content loaded by JavaScript is particularly hard.
State Management: Ensuring the agent has an accurate understanding of the current web page state.
Error Handling: What if an action fails? What if the LLM returns malformed JSON?
Idempotency & Determinism: Hard to achieve with LLMs, making debugging tricky.

Phase 1: Setup and Persona Generation (UX Researcher Initiates)
Researcher Input:
A UX researcher defines the parameters for the simulation. This includes:
Target website/web application URL.
An example persona (e.g., "Michael, a 42M marketing manager, income $75k").
Target demographic distributions (e.g., "generate 50% female personas, 20% low-income").
The overall task/intent for the simulated users (e.g., "Buy a jacket," "Find information about X").
Persona Generation Module:
The system uses the Persona Generator Module.
This module takes the researcher's example persona and demographic constraints.
It makes LLM calls (using prompts like in Appendix A.1) to generate a specified number of unique personas that fit the criteria. For example, it might generate "Sarah, a 35F teacher, income $45k" or "David, a 28M student, income $20k."
Each generated persona includes details like age, gender, profession, income, shopping habits, and personal style, which will influence their behavior.
Phase 2: Simulation Run (For Each LLM Agent/Persona)
This phase is repeated for each generated persona.
Agent Initialization:
An LLM Agent instance is created and "embodied" with one of the generated personas.
The agent's Memory Stream is initialized (it's empty at the start of a session).
The agent is given its primary intent (e.g., "I want to buy a high-quality massage lotion"). This intent is added to its Memory Stream.
The Universal Browser Connector (UBC) is initialized and pointed to the target website's starting URL.
--- Start of the Agent's Interaction Loop ---
The agent now enters an iterative loop of perceiving, planning, and acting. The Fast Loop handles immediate interactions, while the Slow Loop handles deeper, less frequent "thought" processes.
Fast Loop Steps (Repeated for each interaction cycle):
Perception (Agent "Sees" the Webpage):
UBC - Get Page State: The UBC, using Selenium, accesses the current raw HTML of the webpage the agent is on.
UBC - Simplify HTML: The raw HTML is parsed and simplified according to the predefined "recipe." This creates a structured, simplified representation of the page, including:
A simplified HTML tree (text, key elements).
A list of clickables (buttons, links with their generated hierarchical names like search_results.product_name.view_details).
A list of inputs (text fields, dropdowns with their names).
Perception Module - Generate Observations:
The simplified page representation is fed to the Perception Module.
This module uses an LLM (with prompts like Appendix A.2) to "read" the simplified HTML and generate natural language observations about what's visible and interactable (e.g., "I see a search box labeled 'Search'", "There is a product listing for 'Eco-Friendly T-Shirt' priced at $25").
These observations are added to the agent's Memory Stream with timestamps.
Planning (Agent "Decides" What to Do Next - System 1 Thinking):
Planning Module - Retrieve Context: The Planning Module retrieves relevant information from the Memory Stream. This includes:
The agent's persona.
The agent's overall intent.
Recent observations from the Perception Module.
The current state of its plan (if any).
Relevant reflections or wonders (if any from the Slow Loop).
Planning Module - Formulate/Update Plan:
Using an LLM (with prompts like Appendix A.3), the Planning Module generates or updates a short-term plan. This plan includes:
A rationale (e.g., "I need to find the search bar to start looking for a jacket").
A list of plan steps (e.g., "1. Search for 'jacket'. 2. Review search results. 3. Select a suitable jacket...").
The immediate next_step to be executed (e.g., "Search for 'jacket'").
This planning information (rationale, plan, next_step) is added to the Memory Stream.
Action (Agent "Interacts" with the Webpage):
Action Module - Retrieve Context: The Action Module gets the next_step from the Planning Module, the current simplified environment state (from Perception or re-fetched by UBC), persona, intent, and relevant memories.
Action Module - Translate Plan to Action:
Using an LLM (with prompts like Appendix A.4), the Action Module translates the natural language next_step into one or more concrete, predefined browser actions (e.g., {"type": "type_and_submit", "name": "search_input_field", "text": "jacket", "description": "Typing 'jacket' into search and submitting"}).
These action objects are added to the Memory Stream as an action_taken memory. This also forms the Action Trace.
UBC - Execute Action:
The generated action(s) are sent to the Universal Browser Connector.
The UBC uses Selenium to execute these actions on the real web browser (e.g., driver.find_element_by_name("search_input_field").send_keys("jacket") followed by a submit).
The webpage state changes as a result of the action.
Slow Loop Steps (Run periodically or in parallel, less frequently than the Fast Loop):
Reflection (Agent "Thinks Deeply" - System 2 Thinking):
Reflection Module - Retrieve Context: Periodically, the Reflection Module retrieves a set of recent memories (observations, actions, plan updates) from the Memory Stream.
Reflection Module - Generate Insights:
Using an LLM (with prompts like Appendix A.5), it generates high-level insights, preferences, or strategic thoughts based on the agent's persona and recent experiences (e.g., "I've noticed most jackets are out of my budget," "I prefer products with good reviews").
These reflections are added to the Memory Stream. These reflections can then influence future planning in the Fast Loop.
Wonder (Agent "Has Spontaneous Thoughts"):
Wonder Module - Retrieve Context: The Wonder Module also accesses the persona and recent memories.
Wonder Module - Generate Wonders:
Using an LLM (with prompts like Appendix A.6), it generates spontaneous, sometimes unrelated thoughts or "wonders" (e.g., "I wonder what the weather will be like tomorrow," "Maybe I should look for eco-friendly options").
These wonders are added to the Memory Stream, adding to the realism and potentially uncovering unexpected interaction paths.
--- End of the Agent's Interaction Loop ---
Loop Termination:
The Fast Loop (Perception -> Planning -> Action) continues until:
The agent's plan indicates the task/intent is completed (e.g., a purchase is made, information is found).
The agent decides to terminate the session (e.g., cannot find the item, gets frustrated – this would be part of its plan).
A predefined step limit or time limit is reached.
Phase 3: Data Collection and Storage (Per Agent)
Logging Results:
Once an agent's session ends, the system collects:
The complete Action Trace: A sequential log of all actions taken by the agent (e.g., click search_box, type 'massage lotion', click product_link).
The complete Reasoning Trace: The entire content of the agent's Memory Stream for that session (observations, plans, rationales, reflections, wonders).
The Final Session Outcome (e.g., "Task Completed: Purchased item X," "Task Aborted: Could not find suitable item").
(Optionally) A Simulation Video Replay could be generated by screen-recording the Selenium browser or by replaying actions and capturing screenshots.
Phase 4: UX Researcher Analysis (After all simulations)
Accessing Simulation Data:
The UX researcher now has access to the collected data from all simulated agent sessions.
Using the Simulation Replay Interface:
The researcher can load an agent's Action Trace into the Simulation Replay Interface.
This interface replays the agent's actions step-by-step within the actual web environment, highlighting the elements the agent interacted with. The researcher can pause, inspect page details, and understand the agent's behavioral flow.
Using the Agent Interview Interface:
The researcher can select an agent's persona, Action Trace, and Reasoning Trace to load into the Agent Interview Interface.
The researcher can then "chat" with the simulated agent. When the researcher types a question (e.g., "Why did you click on that button?", "What did you think of the checkout process?"):
The interface uses an LLM.
The LLM is provided with the agent's persona, its full Memory Stream (Reasoning Trace) from the session, and the researcher's question as context.
The LLM generates a response as if it were that agent, drawing upon its "memories" and persona.
The researcher can also upload image mockups of new designs to get the "agent's" feedback.
Deriving Insights:
By reviewing the quantitative data (e.g., task completion rates, number of steps) and qualitative data (action traces, reasoning traces, interview responses, video replays), the UX researcher aims to:
Identify potential usability issues in the web design.
Evaluate the effectiveness of their usability testing study design itself (e.g., "Are the tasks clear? Is the chosen persona group appropriate?").
Iterate on the study design or the web design before conducting studies with real human participants.
This detailed flow shows how UXAgent leverages LLMs at multiple stages to simulate diverse user behaviors and provide rich, multimodal data for UX researchers.