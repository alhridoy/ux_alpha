
import { backendService } from './backendService';
import { toast } from 'sonner';
import { z } from 'zod';

/**
 * Service for connecting to and using Stagehand for browser automation
 */
export class StagehandConnector {
  private apiKey: string | null = null;
  private isInitialized = false;
  
  /**
   * Configure the Stagehand connector with an API key
   * @param apiKey - The Stagehand API key
   */
  async configure(apiKey: string): Promise<boolean> {
    try {
      // Send API key to backend
      const success = await backendService.setStagehandApiKey(apiKey);
      
      if (success) {
        this.apiKey = apiKey;
        toast.success("Stagehand API key configured successfully");
        return true;
      } else {
        toast.error("Failed to configure Stagehand API key");
        return false;
      }
    } catch (error) {
      console.error('Error configuring Stagehand:', error);
      toast.error("An error occurred while configuring Stagehand");
      return false;
    }
  }
  
  /**
   * Check if Stagehand is configured
   */
  async isConfigured(): Promise<boolean> {
    try {
      const configured = await backendService.isStagehandConfigured();
      return configured;
    } catch (error) {
      console.error('Error checking Stagehand configuration:', error);
      return false;
    }
  }
  
  /**
   * Initialize Stagehand for a new session
   */
  async initialize(): Promise<boolean> {
    if (!(await this.isConfigured())) {
      toast.error("Stagehand is not configured. Please set an API key first.");
      return false;
    }
    
    try {
      // Initialize Stagehand through the backend
      const result = await backendService.initializeStagehand();
      this.isInitialized = result.success;
      return result.success;
    } catch (error) {
      console.error('Error initializing Stagehand:', error);
      toast.error("Failed to initialize Stagehand");
      return false;
    }
  }
  
  /**
   * Navigate to a URL using Stagehand
   * @param url - The URL to navigate to
   */
  async navigate(url: string): Promise<any> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    try {
      const result = await backendService.stagehandNavigate(url);
      return result;
    } catch (error) {
      console.error('Error navigating with Stagehand:', error);
      return {
        success: false,
        message: `Failed to navigate to ${url}: ${error}`,
      };
    }
  }
  
  /**
   * Execute an action using Stagehand's observe + act pattern
   * @param instruction - Natural language instruction to execute
   */
  async executeAction(instruction: string): Promise<any> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    try {
      const result = await backendService.stagehandExecuteAction(instruction);
      return result;
    } catch (error) {
      console.error('Error executing action with Stagehand:', error);
      return {
        success: false,
        message: `Failed to execute action: ${error}`,
      };
    }
  }
  
  /**
   * Extract data from the page using Stagehand
   * @param instruction - What data to extract
   * @param schema - Zod schema for the data structure
   */
  async extractData(instruction: string, schema: z.ZodType): Promise<any> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    try {
      return await backendService.extractWithStagehand(
        "current_page", // Placeholder, backend should know the current page
        instruction,
        schema
      );
    } catch (error) {
      console.error('Error extracting data with Stagehand:', error);
      throw error;
    }
  }
  
  /**
   * Close the Stagehand session
   */
  async close(): Promise<boolean> {
    if (!this.isInitialized) {
      return true;
    }
    
    try {
      const result = await backendService.closeStagehand();
      if (result.success) {
        this.isInitialized = false;
      }
      return result.success;
    } catch (error) {
      console.error('Error closing Stagehand session:', error);
      return false;
    }
  }
}

// Export a singleton instance
export const stagehandConnector = new StagehandConnector();
