import { AgentAction, Persona, SimulationResult } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Service for interacting with the UXAgent backend API
 */
export class BackendService {
  /**
   * Configure an LLM provider API key
   * @param provider - The provider name (e.g., "openai")
   * @param key - The API key
   * @param model - Optional model name
   */
  async setApiKey(provider: string, key: string, model?: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config/apikey`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider,
          key,
          model,
        }),
      });
      
      const data = await response.json();
      return data.success === true;
    } catch (error) {
      console.error('Error setting API key:', error);
      return false;
    }
  }
  
  /**
   * Get configured LLM providers
   */
  async getConfiguredProviders(): Promise<string[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config/providers`);
      const data = await response.json();
      return data.providers || [];
    } catch (error) {
      console.error('Error getting providers:', error);
      return [];
    }
  }
  
  /**
   * Generate personas using the LLM
   * @param count - Number of personas to generate
   * @param config - Optional configuration
   */
  async generatePersonas(count: number = 1, config?: any): Promise<Persona[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/personas/generate?count=${count}`, 
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(config || {}),
        }
      );
      
      const data = await response.json();
      
      if (!data.success) {
        console.error('Error generating personas:', data.message);
        return [];
      }
      
      return data.personas;
    } catch (error) {
      console.error('Error generating personas:', error);
      return [];
    }
  }
  
  /**
   * Start a new simulation
   * @param personaId - ID of the persona to use
   * @param webUrl - URL to navigate to
   * @param task - Task description
   */
  async startSimulation(personaId: string, webUrl: string, task: string): Promise<string | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulations/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          personaId,
          webUrl,
          task,
          maxCycles: 15,
        }),
      });
      
      const data = await response.json();
      
      if (!data.success) {
        console.error('Error starting simulation:', data.message);
        return null;
      }
      
      return data.simulationId;
    } catch (error) {
      console.error('Error starting simulation:', error);
      return null;
    }
  }
  
  /**
   * Get the status of a simulation
   * @param simulationId - ID of the simulation
   */
  async getSimulationStatus(simulationId: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulations/${simulationId}/status`);
      return await response.json();
    } catch (error) {
      console.error('Error getting simulation status:', error);
      return null;
    }
  }
  
  /**
   * Get the result of a simulation
   * @param simulationId - ID of the simulation
   */
  async getSimulationResult(simulationId: string): Promise<SimulationResult | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulations/${simulationId}`);
      
      if (!response.ok) {
        console.error('Error getting simulation result:', response.statusText);
        return null;
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting simulation result:', error);
      return null;
    }
  }
  
  /**
   * List all simulations
   * @param limit - Maximum number of simulations to return
   * @param offset - Pagination offset
   */
  async listSimulations(limit: number = 10, offset: number = 0): Promise<SimulationResult[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulations?limit=${limit}&offset=${offset}`);
      const data = await response.json();
      return data.simulations || [];
    } catch (error) {
      console.error('Error listing simulations:', error);
      return [];
    }
  }
  
  /**
   * Interview an agent about their experience
   * @param simulationId - ID of the simulation
   * @param message - Message to send to the agent
   */
  async interviewAgent(simulationId: string, message: string): Promise<string | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interview/${simulationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: message,
        }),
      });
      
      const data = await response.json();
      
      if (!data.success) {
        console.error('Error interviewing agent:', data.message);
        return null;
      }
      
      return data.response;
    } catch (error) {
      console.error('Error interviewing agent:', error);
      return null;
    }
  }

  /**
   * Configure browser automation type
   * @param type - The automation type ('selenium' or 'stagehand')
   */
  async configureBrowserAutomation(type: 'selenium' | 'stagehand'): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config/browser`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type }),
      });
      
      const data = await response.json();
      return data.success === true;
    } catch (error) {
      console.error('Error configuring browser automation:', error);
      return false;
    }
  }

  /**
   * Get the current browser automation configuration
   */
  async getBrowserAutomationType(): Promise<'selenium' | 'stagehand' | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config/browser`);
      const data = await response.json();
      return data.type || null;
    } catch (error) {
      console.error('Error getting browser automation type:', error);
      return null;
    }
  }

  /**
   * Configure Stagehand API key
   * @param key - The Stagehand API key
   */
  async setStagehandApiKey(key: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config/stagehand`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ key }),
      });
      
      const data = await response.json();
      return data.success === true;
    } catch (error) {
      console.error('Error setting Stagehand API key:', error);
      return false;
    }
  }

  /**
   * Check if Stagehand API key is configured
   */
  async isStagehandConfigured(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config/stagehand/status`);
      const data = await response.json();
      return data.configured === true;
    } catch (error) {
      console.error('Error checking Stagehand configuration:', error);
      return false;
    }
  }

  /**
   * Extract data from a website using Stagehand
   * @param url - The URL to extract data from
   * @param instruction - Instruction for what data to extract
   * @param schemaDefinition - JSON schema definition for the data structure
   */
  async extractWithStagehand(url: string, instruction: string, schemaDefinition: any): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stagehand/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          instruction,
          schemaDefinition,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.extractedData;
    } catch (error) {
      console.error('Error extracting data with Stagehand:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export const backendService = new BackendService();
