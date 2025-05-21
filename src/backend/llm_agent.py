
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from memory_stream import MemoryStream
from universal_browser_connector import UniversalBrowserConnector
import openai
import os

class LLMAgent:
    """
    The main LLM Agent that orchestrates the two-loop architecture:
    1. Fast Loop: Perception -> Planning -> Action
    2. Slow Loop: Reflection -> Wonder
    """
    
    def __init__(
        self,
        memory_stream: Optional[MemoryStream] = None,
        browser_connector: Optional[UniversalBrowserConnector] = None,
        llm_provider: str = "openai",
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None
    ):
        """
        Initialize the LLM Agent.
        
        Args:
            memory_stream: MemoryStream instance (creates new one if None)
            browser_connector: UniversalBrowserConnector instance (creates new one if None)
            llm_provider: LLM provider to use ("openai", "anthropic", etc.)
            model_name: Model name to use
            api_key: API key for the LLM provider
        """
        self.memory_stream = memory_stream or MemoryStream()
        self.browser_connector = browser_connector or UniversalBrowserConnector(headless=False)
        
        self.llm_provider = llm_provider
        self.model_name = model_name
        
        # Set up LLM client
        if api_key:
            if llm_provider == "openai":
                openai.api_key = api_key
                self.llm_client = openai.Client(api_key=api_key)
            # Add other providers as needed
        else:
            # Try to get from environment variable
            if llm_provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self.llm_client = openai.Client(api_key=api_key)
                else:
                    raise ValueError("No API key provided for OpenAI")
        
        self.logger = logging.getLogger(__name__)
        self.persona = {}
        self.intent = ""
        
        # Keep track of current plan
        self.current_plan = ""
        self.next_step = ""
        
        # Settings for memory retrieval
        self.perception_weights = {
            'importance': 0.3,
            'relevance': 0.4,
            'recency': 0.3,
            'type_weights': {
                'observation': 1.2,
                'action_taken': 1.0,
                'plan_step': 0.8,
                'reflection': 0.7,
                'wonder': 0.5,
                'persona_detail': 1.0,
                'intent': 1.5
            }
        }
        
        self.planning_weights = {
            'importance': 0.3,
            'relevance': 0.5,
            'recency': 0.2,
            'type_weights': {
                'observation': 1.0,
                'action_taken': 1.2,
                'plan_step': 1.5,
                'reflection': 0.8,
                'wonder': 0.3,
                'persona_detail': 0.7,
                'intent': 1.4
            }
        }
        
        self.action_weights = {
            'importance': 0.35,
            'relevance': 0.45,
            'recency': 0.2,
            'type_weights': {
                'observation': 0.9,
                'action_taken': 0.7,
                'plan_step': 1.5,
                'reflection': 0.5,
                'wonder': 0.3,
                'persona_detail': 0.6,
                'intent': 1.3
            }
        }
    
    def set_persona(self, persona: Dict[str, Any]) -> None:
        """
        Set the persona for this agent.
        
        Args:
            persona: Dictionary containing persona details
        """
        self.persona = persona
        
        # Add persona details to memory stream
        for key, value in persona.items():
            if isinstance(value, str):
                self.memory_stream.add_memory(
                    memory_type="persona_detail",
                    content=f"{key}: {value}",
                    source_module="PersonaLoader",
                    importance_score=8.0
                )
            elif isinstance(value, list):
                for item in value:
                    self.memory_stream.add_memory(
                        memory_type="persona_detail",
                        content=f"{key}: {item}",
                        source_module="PersonaLoader",
                        importance_score=8.0
                    )
    
    def set_intent(self, intent: str) -> None:
        """
        Set the intent/goal for this agent's browsing session.
        
        Args:
            intent: String describing what the agent aims to accomplish
        """
        self.intent = intent
        
        # Add intent to memory stream
        self.memory_stream.add_memory(
            memory_type="intent",
            content=f"My goal is to: {intent}",
            source_module="IntentLoader",
            importance_score=10.0
        )
    
    def start_session(self, url: str) -> Dict[str, Any]:
        """
        Start a browsing session by navigating to the initial URL.
        
        Args:
            url: Starting URL for the browsing session
            
        Returns:
            Result of the navigation action
        """
        # Make sure persona and intent are set
        if not self.persona:
            raise ValueError("Persona must be set before starting a session")
        if not self.intent:
            raise ValueError("Intent must be set before starting a session")
        
        # Navigate to the URL
        result = self.browser_connector.navigate(url)
        
        # Add the navigation action to memory
        self.memory_stream.add_memory(
            memory_type="action_taken",
            content=f"Navigated to {url}",
            source_module="Agent",
            importance_score=7.0
        )
        
        return result
    
    def run_fast_loop_cycle(self) -> Dict[str, Any]:
        """
        Run one cycle of the fast loop: Perception -> Planning -> Action.
        
        Returns:
            Result of the action taken
        """
        # 1. Run perception module
        observations = self._run_perception_module()
        
        # 2. Run planning module
        plan_result = self._run_planning_module()
        
        # 3. Run action module
        action_result = self._run_action_module()
        
        return action_result
    
    def _run_perception_module(self) -> List[str]:
        """
        Run the perception module to observe the current environment.
        
        Returns:
            List of observation strings
        """
        self.logger.info("Running perception module")
        
        # Get current page state from browser connector
        current_page = self.browser_connector.simplify_html()
        
        # Prepare the prompt for perception
        prompt = self._create_perception_prompt(current_page)
        
        # Call LLM to generate observations
        try:
            response = self._call_llm(prompt)
            if not response:
                return []
                
            # Parse the JSON response
            observations = self._parse_json_response(response, 'observations')
            
            # If parsing fails, try to extract observations manually
            if not observations:
                # Try to extract list items manually if JSON parsing failed
                observations = self._extract_list_items(response)
            
            # Add observations to memory
            for observation in observations:
                # Score the importance based on relevance to intent
                importance_score = self._score_observation_importance(observation)
                
                self.memory_stream.add_memory(
                    memory_type="observation",
                    content=observation,
                    source_module="PerceptionModule",
                    importance_score=importance_score
                )
            
            return observations
            
        except Exception as e:
            self.logger.error(f"Error in perception module: {str(e)}")
            return []
    
    def _create_perception_prompt(self, page_state: Dict[str, Any]) -> str:
        """Create the prompt for the perception module."""
        # Format page data for the prompt
        clickables_text = "\n".join([f"- {c['name']}: {c['description']}" for c in page_state.get('clickables', [])])
        inputs_text = "\n".join([f"- {i['name']}: {i['description']}" for i in page_state.get('inputs', [])])
        
        text_blocks = []
        for block in page_state.get('text_blocks', []):
            if block['type'] == 'heading':
                text_blocks.append(f"HEADING: {block['text']}")
            elif block['type'] == 'paragraph':
                text_blocks.append(f"PARAGRAPH: {block['text']}")
            elif block['type'] == 'list':
                items_text = "\n  * " + "\n  * ".join(block['items'])
                text_blocks.append(f"LIST:{items_text}")
                
        text_blocks_text = "\n\n".join(text_blocks)
        
        # Construct the prompt
        prompt = f"""
You are the PERCEIVE module of a web browsing agent. Your job is to carefully observe the current web page and generate meaningful observations.

The web page is at URL: {page_state['url']}
Title: {page_state['title']}

CLICKABLE ELEMENTS:
{clickables_text}

INPUT ELEMENTS:
{inputs_text}

TEXT CONTENT:
{text_blocks_text}

Based on what you see on this page, list all observations that would be relevant to a user with this profile:
{self._format_persona_for_prompt()}

Their current goal is: {self.intent}

Generate at least 3-7 observations that note important features, content, options, or potential issues on the page. Focus on what would be most relevant to the user's goal.

Output as a JSON object: {{'observations': ['<obs1>', '<obs2>', ...]}}
"""
        return prompt
    
    def _run_planning_module(self) -> Dict[str, Any]:
        """
        Run the planning module to create or update the plan.
        
        Returns:
            Dict containing rationale, plan and next step
        """
        self.logger.info("Running planning module")
        
        # Retrieve relevant memories for planning
        relevant_memories = self.memory_stream.retrieve_memories(
            query_text=f"Current situation and how to accomplish: {self.intent}",
            weights=self.planning_weights,
            num_memories=10
        )
        
        # Prepare the prompt for planning
        prompt = self._create_planning_prompt(relevant_memories)
        
        # Call LLM to generate plan
        try:
            response = self._call_llm(prompt)
            if not response:
                return {'rationale': '', 'plan': self.current_plan, 'next_step': self.next_step}
                
            # Parse the JSON response
            plan_result = self._parse_json_response(response, ['rationale', 'plan', 'next_step'])
            
            if not plan_result:
                self.logger.error(f"Failed to parse planning response: {response}")
                return {'rationale': '', 'plan': self.current_plan, 'next_step': self.next_step}
                
            # Update current plan and next step
            self.current_plan = plan_result.get('plan', self.current_plan)
            self.next_step = plan_result.get('next_step', self.next_step)
            
            # Add plan step to memory
            self.memory_stream.add_memory(
                memory_type="plan_step",
                content=f"Plan: {self.current_plan}\nNext step: {self.next_step}",
                source_module="PlanningModule",
                importance_score=8.0
            )
            
            return plan_result
            
        except Exception as e:
            self.logger.error(f"Error in planning module: {str(e)}")
            return {'rationale': '', 'plan': self.current_plan, 'next_step': self.next_step}
    
    def _create_planning_prompt(self, relevant_memories: List[Dict[str, Any]]) -> str:
        """Create the prompt for the planning module."""
        # Format memories for the prompt
        memories_text = self._format_memories_for_prompt(relevant_memories)
        
        # Construct the prompt
        prompt = f"""
You are tasked with creating/updating a detailed plan for a web browsing agent with the following persona:
{self._format_persona_for_prompt()}

INTENT:
{self.intent}

RELEVANT MEMORIES:
{memories_text}

PREVIOUS PLAN (if any):
{self.current_plan}

Based on the persona, intent, and memories, create or update a plan to accomplish the goal.
Think step by step about the most effective way to navigate the website and complete the task.
Be specific about what actions to take next.

Output as a JSON object with the following structure:
{{
  "rationale": "Explain why this plan makes sense given the current situation",
  "plan": "Step 1: ...\nStep 2: ...\nStep 3: ...",
  "next_step": "The specific next step that should be executed now (just one action)"
}}

Your output MUST be valid JSON.
"""
        return prompt
    
    def _run_action_module(self) -> Dict[str, Any]:
        """
        Run the action module to determine and execute the next action.
        
        Returns:
            Result of the action execution
        """
        self.logger.info("Running action module")
        
        # Get current page state
        current_page = self.browser_connector.simplify_html()
        
        # Retrieve relevant memories for action selection
        relevant_memories = self.memory_stream.retrieve_memories(
            query_text=f"How to execute this step: {self.next_step}",
            weights=self.action_weights,
            num_memories=7
        )
        
        # Prepare the prompt for action selection
        prompt = self._create_action_prompt(current_page, relevant_memories)
        
        # Call LLM to generate action
        try:
            response = self._call_llm(prompt)
            if not response:
                return {'success': False, 'message': 'Failed to generate action'}
                
            # Parse the JSON response
            action_result = self._parse_json_response(response, 'actions')
            
            if not action_result or not isinstance(action_result, list) or not action_result:
                self.logger.error(f"Failed to parse action response: {response}")
                return {'success': False, 'message': 'Failed to parse action response'}
                
            # Execute the actions
            for action in action_result:
                # Log the action
                action_description = self._describe_action(action)
                self.memory_stream.add_memory(
                    memory_type="action_taken",
                    content=action_description,
                    source_module="ActionModule",
                    importance_score=8.0,
                    metadata=action
                )
                
                # Execute the action
                result = self.browser_connector.execute_action(action)
                
                # If the action fails, stop execution
                if not result.get('success', False):
                    self.memory_stream.add_memory(
                        memory_type="action_taken",
                        content=f"Action failed: {result.get('message', 'Unknown error')}",
                        source_module="ActionModule",
                        importance_score=9.0
                    )
                    return result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in action module: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _create_action_prompt(self, page_state: Dict[str, Any], relevant_memories: List[Dict[str, Any]]) -> str:
        """Create the prompt for the action module."""
        # Format page data for the prompt
        clickables_text = "\n".join([f"- {c['name']}: {c['description']}" for c in page_state.get('clickables', [])])
        inputs_text = "\n".join([f"- {i['name']}: {i['description']}" for i in page_state.get('inputs', [])])
        
        # Format memories for the prompt
        memories_text = self._format_memories_for_prompt(relevant_memories)
        
        # Construct the prompt
        prompt = f"""
You are the ACTION module of a web browsing agent. Your job is to translate the current plan step into specific actions that can be executed on the web page.

PERSONA:
{self._format_persona_for_prompt()}

INTENT:
{self.intent}

CURRENT PLAN STEP:
{self.next_step}

ENVIRONMENT:
URL: {page_state['url']}
Title: {page_state['title']}

CLICKABLE ELEMENTS:
{clickables_text}

INPUT ELEMENTS:
{inputs_text}

RELEVANT MEMORIES:
{memories_text}

Translate the current plan step into ONE specific action that can be executed on the web page.
Choose from these action types:
1. click - Click on a clickable element
2. input - Enter text into an input element
3. scroll - Scroll the page (value: "up", "down", "top", or "bottom")
4. navigate - Go to a specific URL
5. back - Go back to the previous page
6. wait - Wait for a specified number of seconds

Output as a JSON array with a SINGLE action object:
{{
  "actions": [
    {{
      "type": "click|input|scroll|navigate|back|wait",
      "name": "element_name (for click/input)",
      "value": "text to input or scroll direction",
      "description": "Human-readable description of what this action accomplishes"
    }}
  ]
}}

Your output MUST be valid JSON.
"""
        return prompt
    
    def _describe_action(self, action: Dict[str, Any]) -> str:
        """Generate a human-readable description of an action."""
        action_type = action.get('type', '').lower()
        
        if action_type == 'click':
            return f"Clicked on {action.get('name', 'unknown element')}: {action.get('description', '')}"
        elif action_type == 'input':
            return f"Entered text '{action.get('value', '')}' into {action.get('name', 'unknown element')}"
        elif action_type == 'scroll':
            return f"Scrolled {action.get('value', 'down')} on the page"
        elif action_type == 'navigate':
            return f"Navigated to URL: {action.get('target', '')}"
        elif action_type == 'back':
            return "Navigated back to previous page"
        elif action_type == 'wait':
            return f"Waited for {action.get('value', 2)} seconds"
        else:
            return f"Unknown action: {action_type}"
    
    def run_reflection_module(self) -> List[str]:
        """
        Run the reflection module to generate insights.
        
        Returns:
            List of reflection strings
        """
        self.logger.info("Running reflection module")
        
        # Get recent memories (focus on observations and actions)
        recent_memories = []
        for memory_type in ["observation", "action_taken", "plan_step"]:
            type_memories = self.memory_stream.get_memories_by_type(memory_type)
            # Sort by timestamp (descending) and take the most recent ones
            type_memories.sort(key=lambda m: m.get('timestamp', 0), reverse=True)
            recent_memories.extend(type_memories[:10])
        
        # Sort combined memories by timestamp (descending)
        recent_memories.sort(key=lambda m: m.get('timestamp', 0), reverse=True)
        recent_memories = recent_memories[:15]  # Limit to 15 most recent
        
        # Prepare the prompt for reflection
        prompt = self._create_reflection_prompt(recent_memories)
        
        # Call LLM to generate reflections
        try:
            response = self._call_llm(prompt)
            if not response:
                return []
                
            # Parse the JSON response
            reflections = self._parse_json_response(response, 'insights')
            
            # If parsing fails, try to extract list items manually
            if not reflections:
                reflections = self._extract_list_items(response)
            
            # Add reflections to memory
            for reflection in reflections:
                self.memory_stream.add_memory(
                    memory_type="reflection",
                    content=reflection,
                    source_module="ReflectionModule",
                    importance_score=7.0
                )
            
            return reflections
            
        except Exception as e:
            self.logger.error(f"Error in reflection module: {str(e)}")
            return []
    
    def _create_reflection_prompt(self, recent_memories: List[Dict[str, Any]]) -> str:
        """Create the prompt for the reflection module."""
        # Format memories for the prompt
        memories_text = self._format_memories_for_prompt(recent_memories)
        
        # Construct the prompt
        prompt = f"""
You are the REFLECTION module of a web browsing agent. Your job is to generate high-level insights and reflections based on recent memories and the agent's persona.

PERSONA:
{self._format_persona_for_prompt()}

INTENT:
{self.intent}

RECENT MEMORIES:
{memories_text}

Based on these memories and the persona, generate 3-5 thoughtful reflections or insights about the experience so far.
These should be higher-level thoughts that connect observations and actions to the persona's characteristics and goals.

Examples:
- "I'm finding this site's navigation confusing since there are too many options, which is frustrating given my limited technical experience."
- "The product descriptions are very detailed, which I appreciate as someone who likes to make informed decisions."
- "This checkout process has multiple steps which is making me anxious about making a mistake."

Output as a JSON object:
{{
  "insights": [
    "reflection 1",
    "reflection 2",
    "reflection 3"
  ]
}}

Your output MUST be valid JSON.
"""
        return prompt
    
    def run_wonder_module(self) -> List[str]:
        """
        Run the wonder module to generate curiosities and questions.
        
        Returns:
            List of wonder strings
        """
        self.logger.info("Running wonder module")
        
        # Get recent memories (focus on observations and reflections)
        recent_memories = []
        for memory_type in ["observation", "reflection", "action_taken"]:
            type_memories = self.memory_stream.get_memories_by_type(memory_type)
            # Sort by timestamp (descending) and take the most recent ones
            type_memories.sort(key=lambda m: m.get('timestamp', 0), reverse=True)
            recent_memories.extend(type_memories[:5])
        
        # Sort combined memories by timestamp (descending)
        recent_memories.sort(key=lambda m: m.get('timestamp', 0), reverse=True)
        recent_memories = recent_memories[:10]  # Limit to 10 most recent
        
        # Prepare the prompt for wonder
        prompt = self._create_wonder_prompt(recent_memories)
        
        # Call LLM to generate wonders
        try:
            response = self._call_llm(prompt)
            if not response:
                return []
                
            # Parse the JSON response
            wonders = self._parse_json_response(response, 'thoughts')
            
            # If parsing fails, try to extract list items manually
            if not wonders:
                wonders = self._extract_list_items(response)
            
            # Add wonders to memory
            for wonder in wonders:
                self.memory_stream.add_memory(
                    memory_type="wonder",
                    content=wonder,
                    source_module="WonderModule",
                    importance_score=4.0
                )
            
            return wonders
            
        except Exception as e:
            self.logger.error(f"Error in wonder module: {str(e)}")
            return []
    
    def _create_wonder_prompt(self, recent_memories: List[Dict[str, Any]]) -> str:
        """Create the prompt for the wonder module."""
        # Format memories for the prompt
        memories_text = self._format_memories_for_prompt(recent_memories)
        
        # Construct the prompt
        prompt = f"""
You are the WONDER module of a web browsing agent. Your job is to generate random thoughts, curiosities, and questions that might cross the persona's mind.

PERSONA:
{self._format_persona_for_prompt()}

INTENT:
{self.intent}

RECENT MEMORIES:
{memories_text}

Based on these memories and the persona, generate 2-3 random thoughts or questions that might naturally occur to this persona.
These should feel natural and reflect the persona's characteristics, preferences, and curiosities.

Examples:
- "I wonder if they offer free shipping for orders over a certain amount?"
- "Would the blue color option match my living room better than the gray one?"
- "I'm not sure if I should check reviews on another site before making a decision."

Output as a JSON object:
{{
  "thoughts": [
    "thought 1",
    "thought 2"
  ]
}}

Your output MUST be valid JSON.
"""
        return prompt
    
    def _format_persona_for_prompt(self) -> str:
        """Format the persona details for inclusion in prompts."""
        if not self.persona:
            return "No persona defined"
            
        persona_text = []
        for key, value in self.persona.items():
            if isinstance(value, list):
                persona_text.append(f"{key}: {', '.join(value)}")
            else:
                persona_text.append(f"{key}: {value}")
                
        return "\n".join(persona_text)
    
    def _format_memories_for_prompt(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories for inclusion in prompts."""
        if not memories:
            return "No relevant memories"
            
        # Sort memories by timestamp (newest first)
        memories = sorted(memories, key=lambda m: m.get('timestamp', 0), reverse=True)
        
        memory_texts = []
        for memory in memories:
            timestamp_str = time.strftime('%H:%M:%S', time.localtime(memory.get('timestamp', 0)))
            memory_texts.append(f"[{timestamp_str} | {memory.get('type', 'unknown')}] {memory.get('content', '')}")
            
        return "\n".join(memory_texts)
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            # Add other providers as needed
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error calling LLM: {str(e)}")
            return ""
    
    def _parse_json_response(self, response: str, expected_keys: Union[str, List[str]]) -> Any:
        """Parse a JSON response from the LLM, handling potential issues."""
        try:
            # Try to extract JSON block if it's wrapped in markdown code blocks
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # Try to find a JSON object pattern if still not extracted
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
                
            data = json.loads(response)
            
            # Check if the expected keys are present
            if isinstance(expected_keys, str):
                return data.get(expected_keys, None)
            else:
                return {key: data.get(key, None) for key in expected_keys}
                
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse JSON response: {response}")
            return None
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text when JSON parsing fails."""
        items = []
        
        # Look for numbered list items (1. Item)
        number_matches = re.findall(r'\d+\.\s*(.+?)(?=\d+\.|$)', text, re.DOTALL)
        
        # Look for bulleted list items (- Item or * Item)
        bullet_matches = re.findall(r'[-*]\s*(.+?)(?=[-*]|$)', text, re.DOTALL)
        
        # Combine and clean up
        all_matches = number_matches + bullet_matches
        for match in all_matches:
            clean_item = match.strip()
            if clean_item:
                items.append(clean_item)
                
        return items
    
    def _score_observation_importance(self, observation: str) -> float:
        """Score the importance of an observation based on relevance to intent."""
        # In a production system, this would call the LLM to evaluate importance
        # For now, use a simple heuristic based on keyword matching with intent
        
        intent_words = set(self.intent.lower().split())
        observation_words = set(observation.lower().split())
        
        common_words = intent_words.intersection(observation_words)
        
        # Base importance score
        score = 5.0
        
        # Adjust based on word overlap with intent
        if common_words:
            score += min(len(common_words) * 0.5, 3.0)
            
        # Boost score for observations mentioning key UI elements
        ui_keywords = ['button', 'link', 'menu', 'search', 'input', 'form', 'error', 'navigation']
        for keyword in ui_keywords:
            if keyword in observation.lower():
                score += 0.5
                
        return min(max(score, 1.0), 10.0)  # Ensure score is between 1-10
    
    def run_complete_session(self, url: str, max_cycles: int = 10) -> Dict[str, Any]:
        """
        Run a complete session, executing multiple fast loop cycles and slow loop modules.
        
        Args:
            url: Starting URL for the session
            max_cycles: Maximum number of fast loop cycles to run
            
        Returns:
            Dictionary with session results
        """
        # Start session
        self.start_session(url)
        
        for cycle in range(max_cycles):
            self.logger.info(f"Running cycle {cycle+1}/{max_cycles}")
            
            # Run fast loop cycle
            result = self.run_fast_loop_cycle()
            
            # Run slow loop modules periodically
            if cycle > 0 and cycle % 3 == 0:
                self.run_reflection_module()
                self.run_wonder_module()
                
            # Check if we should terminate early
            if self._should_terminate_session():
                break
                
        # Final reflection and wonder
        reflections = self.run_reflection_module()
        wonderings = self.run_wonder_module()
        
        # Return session results
        return {
            'url': url,
            'cycles_completed': cycle + 1,
            'task_completed': self._is_task_completed(),
            'memories': self.memory_stream.get_all_memories(),
            'reflections': reflections,
            'wonderings': wonderings
        }
    
    def _should_terminate_session(self) -> bool:
        """Determine if the session should be terminated early."""
        # Check if task appears to be completed
        if self._is_task_completed():
            return True
            
        # Check for error states or stuckness
        recent_actions = self.memory_stream.get_memories_by_type("action_taken")
        if len(recent_actions) >= 3:
            # Sort by timestamp (most recent first)
            recent_actions.sort(key=lambda m: m.get('timestamp', 0), reverse=True)
            
            # Check if the last few actions failed
            failure_count = 0
            for action in recent_actions[:3]:
                if 'failed' in action.get('content', '').lower():
                    failure_count += 1
                    
            if failure_count >= 2:
                self.logger.info("Terminating session due to multiple failed actions")
                return True
                
        return False
    
    def _is_task_completed(self) -> bool:
        """Determine if the task has been completed."""
        # This is a simplified version - a real implementation would use the LLM
        # to evaluate whether the task has been completed based on the intent and memories
        
        # Get the most recent reflections
        reflections = self.memory_stream.get_memories_by_type("reflection")
        
        # Look for indication of completion in reflections
        for reflection in reflections:
            content = reflection.get('content', '').lower()
            if 'completed' in content and 'task' in content:
                return True
                
        return False
    
    def close(self):
        """Clean up resources."""
        if self.browser_connector:
            self.browser_connector.close()
