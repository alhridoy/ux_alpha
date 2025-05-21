
import { z } from "zod";

/**
 * Service for interacting with Stagehand API for browser automation
 */
export class StagehandService {
  private apiKey: string | null = null;

  /**
   * Set the Stagehand API key
   * @param key - The API key
   */
  setApiKey(key: string) {
    this.apiKey = key;
  }

  /**
   * Get the configured API key
   */
  getApiKey(): string | null {
    return this.apiKey;
  }

  /**
   * Extract data from a website using Stagehand
   * @param webUrl - The URL to extract data from
   * @param instruction - Instruction for what data to extract
   * @param schema - Zod schema defining the structure of data to extract
   */
  async extractData<T>(webUrl: string, instruction: string, schema: z.ZodType<T>): Promise<T | null> {
    if (!this.apiKey) {
      console.error('Stagehand API key not configured');
      return null;
    }

    try {
      // In a production app, this would call the backend API
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/stagehand/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: webUrl,
          instruction,
          schemaDefinition: schema.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      return data.extractedData;
    } catch (error) {
      console.error('Error extracting data with Stagehand:', error);
      return null;
    }
  }
}

// Export a singleton instance
export const stagehandService = new StagehandService();
