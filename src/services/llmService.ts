
import { Persona, AgentAction, SimulationResult } from '@/types';

// Configuration for API calls
type LLMServiceConfig = {
  apiKey: string;
  model: string;
  endpoint: string;
};

// Default configuration using OpenAI's GPT-4
const defaultConfig: LLMServiceConfig = {
  apiKey: '',
  model: 'gpt-4o',
  endpoint: 'https://api.openai.com/v1/chat/completions',
};

// Service class for handling LLM API calls
export class LLMService {
  private config: LLMServiceConfig;

  constructor(config: Partial<LLMServiceConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  // Set or update the API key
  setApiKey(apiKey: string) {
    this.config.apiKey = apiKey;
    return this;
  }

  // Check if the service is properly configured
  isConfigured(): boolean {
    return !!this.config.apiKey;
  }

  // Generate a persona using the LLM
  async generatePersona(prompt: string): Promise<Persona | null> {
    if (!this.isConfigured()) {
      console.error('LLM service is not configured with an API key');
      return null;
    }

    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.model,
          messages: [
            {
              role: 'system',
              content: 'You are a helpful assistant that generates realistic user personas for UX testing. Return only JSON without any explanations.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          response_format: { type: 'json_object' }
        })
      });

      const data = await response.json();
      
      if (data.error) {
        console.error('LLM API error:', data.error);
        return null;
      }

      // Parse the LLM response to extract the persona
      const personaData = JSON.parse(data.choices[0].message.content);
      return personaData;
    } catch (error) {
      console.error('Error generating persona:', error);
      return null;
    }
  }

  // Simulate website interaction using the LLM
  async simulateInteraction(persona: Persona, webUrl: string, task: string): Promise<AgentAction[]> {
    if (!this.isConfigured()) {
      console.error('LLM service is not configured with an API key');
      return [];
    }

    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.model,
          messages: [
            {
              role: 'system',
              content: `You are an AI that simulates how a specific user persona would interact with a website. 
                        Generate a sequence of actions the user would take. Return only JSON without explanations.`
            },
            {
              role: 'user',
              content: `Simulate how this persona would interact with ${webUrl} to accomplish this task: ${task}
                        
                        Persona:
                        Name: ${persona.name}
                        Age: ${persona.age}
                        Occupation: ${persona.occupation}
                        Tech Experience: ${persona.techExperience}
                        Traits: ${persona.traits.join(', ')}
                        Goals: ${persona.goals.join(', ')}
                        Pain Points: ${persona.painPoints.join(', ')}
                        
                        Return a JSON array of action objects with id, timestamp, type, target (if applicable), 
                        value (if applicable), and reasoning fields.`
            }
          ],
          response_format: { type: 'json_object' }
        })
      });

      const data = await response.json();
      
      if (data.error) {
        console.error('LLM API error:', data.error);
        return [];
      }

      // Parse the LLM response to extract the actions
      const actionsData = JSON.parse(data.choices[0].message.content);
      return actionsData.actions;
    } catch (error) {
      console.error('Error simulating interaction:', error);
      return [];
    }
  }

  // Generate post-simulation reflections and wonderings
  async generateReflections(simulation: Partial<SimulationResult>): Promise<{ reflections: string[], wonderings: string[] }> {
    if (!this.isConfigured()) {
      console.error('LLM service is not configured with an API key');
      return { reflections: [], wonderings: [] };
    }

    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.model,
          messages: [
            {
              role: 'system',
              content: `You are an AI that generates reflections and wonderings from a user's perspective after they completed 
                        (or attempted to complete) a task on a website. Return only JSON without explanations.`
            },
            {
              role: 'user',
              content: `Generate reflections and wonderings for this persona after they ${
                simulation.taskCompleted ? 'completed' : 'attempted'} this task: ${simulation.task}
                
                Persona:
                Name: ${simulation.persona?.name}
                Age: ${simulation.persona?.age}
                Occupation: ${simulation.persona?.occupation}
                Tech Experience: ${simulation.persona?.techExperience}
                Traits: ${simulation.persona?.traits.join(', ')}
                
                Return a JSON object with two arrays: 'reflections' (3-5 thoughtful observations about the experience) 
                and 'wonderings' (2-3 questions or thoughts the user might have after the experience).`
            }
          ],
          response_format: { type: 'json_object' }
        })
      });

      const data = await response.json();
      
      if (data.error) {
        console.error('LLM API error:', data.error);
        return { reflections: [], wonderings: [] };
      }

      // Parse the LLM response to extract the reflections and wonderings
      const reflectionData = JSON.parse(data.choices[0].message.content);
      return reflectionData;
    } catch (error) {
      console.error('Error generating reflections:', error);
      return { reflections: [], wonderings: [] };
    }
  }
}

// Export a singleton instance of the service
export const llmService = new LLMService();
