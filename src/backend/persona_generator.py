
import json
import os
from typing import Dict, List, Any, Optional
import openai

class PersonaGenerator:
    """
    Generate realistic user personas for UX testing using LLM.
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None
    ):
        """
        Initialize the PersonaGenerator.
        
        Args:
            llm_provider: LLM provider to use ("openai", "anthropic", etc.)
            model_name: Model name to use
            api_key: API key for the LLM provider
        """
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
    
    def generate_persona(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a single persona based on configuration.
        
        Args:
            config: Configuration dict with constraints like:
                   age_range: "18-25", "26-35", "36-50", "51-70", "70+"
                   gender: "Male", "Female", "Non-binary", "Any"
                   tech_experience: "Beginner", "Intermediate", "Advanced", "Any"
                   income_level: "Low", "Medium", "High", "Any"
                   education_level: "High School", "College", "Graduate", "Any"
                   previous_personas: List of previously generated personas to avoid duplication
                   
        Returns:
            Dictionary containing persona details
        """
        if config is None:
            config = {}
            
        # Default values if not specified
        age_range = config.get('age_range', 'Any')
        gender = config.get('gender', 'Any')
        tech_experience = config.get('tech_experience', 'Any')
        income_level = config.get('income_level', 'Any')
        education_level = config.get('education_level', 'Any')
        previous_personas = config.get('previous_personas', [])
        
        # Create the prompt
        prompt = self._create_generate_persona_prompt(
            age_range, gender, tech_experience, income_level, education_level, previous_personas
        )
        
        # Call the LLM
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that generates realistic user personas for UX testing."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                persona_json = response.choices[0].message.content
                
                # Parse the JSON response
                try:
                    persona = json.loads(persona_json)
                    return persona
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON response: {e}")
                    print(f"Response was: {persona_json}")
                    return self._generate_fallback_persona()
                
            # Add other providers as needed
            
            return self._generate_fallback_persona()
            
        except Exception as e:
            print(f"Error generating persona: {e}")
            return self._generate_fallback_persona()
    
    def generate_multiple_personas(self, count: int = 3, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple unique personas.
        
        Args:
            count: Number of personas to generate
            config: Configuration dict (see generate_persona)
            
        Returns:
            List of persona dictionaries
        """
        if config is None:
            config = {}
            
        personas = []
        for i in range(count):
            # Update config with previously generated personas to ensure diversity
            current_config = config.copy()
            current_config['previous_personas'] = personas
            
            # Generate the persona
            persona = self.generate_persona(current_config)
            personas.append(persona)
            
        return personas
    
    def _create_generate_persona_prompt(
        self, 
        age_range: str,
        gender: str,
        tech_experience: str,
        income_level: str,
        education_level: str,
        previous_personas: List[Dict[str, Any]]
    ) -> str:
        """Create the prompt for persona generation."""
        # Format constraints
        constraints = []
        if age_range != 'Any':
            constraints.append(f"Age range: {age_range}")
        if gender != 'Any':
            constraints.append(f"Gender: {gender}")
        if tech_experience != 'Any':
            constraints.append(f"Tech experience level: {tech_experience}")
        if income_level != 'Any':
            constraints.append(f"Income level: {income_level}")
        if education_level != 'Any':
            constraints.append(f"Education level: {education_level}")
            
        constraints_text = "\n".join([f"- {c}" for c in constraints]) if constraints else "No specific constraints."
        
        # Format previous personas to avoid duplication
        previous_text = ""
        if previous_personas:
            prev_summaries = []
            for i, p in enumerate(previous_personas):
                summary = f"Persona {i+1}: {p.get('name', 'Unknown')}, {p.get('age', 'Unknown')} y/o {p.get('gender', 'Unknown')}, {p.get('occupation', 'Unknown')}"
                prev_summaries.append(summary)
            previous_text = "\n".join(prev_summaries)
        
        # Construct the prompt
        prompt = f"""
Generate a realistic user persona for UX testing with the following properties:

1. Basic Demographics:
   - Full name
   - Age (a specific number, not a range)
   - Gender
   - Location (city, country)
   - Occupation
   - Education level
   - Income bracket

2. Technical Profile:
   - Tech experience level (Beginner, Intermediate, or Advanced)
   - Devices regularly used
   - Hours spent online per week
   - Favorite apps/websites
   - Tech challenges or frustrations

3. Behavioral Traits:
   - 3-5 personality traits relevant to digital interaction
   - Decision-making style
   - Risk tolerance
   - Patience level with technology

4. Goals and Motivations:
   - 2-4 primary user goals when using websites/apps
   - What motivates them to use technology
   - What satisfies them in a digital experience

5. Pain Points:
   - 2-4 specific frustrations when using technology
   - Accessibility needs (if any)
   - Trust concerns with technology

Constraints:
{constraints_text}

Previous personas (create a different persona):
{previous_text}

Return ONLY a JSON object with the following format:
{{
  "name": "Full Name",
  "age": 35,
  "gender": "Gender",
  "location": "City, Country",
  "occupation": "Job Title/Role",
  "education": "Highest Education Level",
  "income": "Income Bracket",
  "techExperience": "Beginner/Intermediate/Advanced",
  "devices": ["Device 1", "Device 2", ...],
  "hoursOnline": 25,
  "favoriteApps": ["App 1", "App 2", ...],
  "techChallenges": ["Challenge 1", "Challenge 2", ...],
  "traits": ["Trait 1", "Trait 2", ...],
  "decisionStyle": "How they make decisions",
  "riskTolerance": "Low/Medium/High",
  "patienceLevel": "Low/Medium/High",
  "goals": ["Goal 1", "Goal 2", ...],
  "motivations": ["Motivation 1", "Motivation 2", ...],
  "painPoints": ["Pain Point 1", "Pain Point 2", ...],
  "accessibilityNeeds": "Any accessibility needs or None",
  "trustConcerns": ["Concern 1", "Concern 2", ...]
}}

Make sure the persona feels realistic, consistent, and has enough specific details to be useful for UX testing.
"""
        return prompt
    
    def _generate_fallback_persona(self) -> Dict[str, Any]:
        """Generate a basic fallback persona when LLM call fails."""
        return {
            "name": "Alex Johnson",
            "age": 35,
            "gender": "Non-binary",
            "location": "Austin, USA",
            "occupation": "Marketing Manager",
            "education": "Bachelor's Degree",
            "income": "$70,000 - $90,000",
            "techExperience": "Intermediate",
            "devices": ["Smartphone", "Laptop", "Tablet"],
            "hoursOnline": 30,
            "favoriteApps": ["Instagram", "Spotify", "Gmail"],
            "techChallenges": ["Remembering passwords", "Learning new interfaces"],
            "traits": ["Curious", "Practical", "Impatient"],
            "decisionStyle": "Research-based, but time-conscious",
            "riskTolerance": "Medium",
            "patienceLevel": "Medium",
            "goals": ["Find information quickly", "Stay connected", "Be productive"],
            "motivations": ["Efficiency", "Social connection", "Professional growth"],
            "painPoints": ["Complex navigation", "Slow loading times", "Too many options"],
            "accessibilityNeeds": "None",
            "trustConcerns": ["Data privacy", "Security breaches"]
        }
