
import { backendService } from './backendService';
import { toast } from 'sonner';

/**
 * Service to handle initial setup and configuration
 */
export class SetupService {
  /**
   * Configure the OpenAI API key if provided
   * @param apiKey - OpenAI API key
   */
  static async setupOpenAIKey(apiKey: string): Promise<boolean> {
    try {
      console.log('Setting up OpenAI API key...');
      const success = await backendService.setApiKey('openai', apiKey, 'gpt-4o');
      
      if (success) {
        toast.success('OpenAI API key configured successfully');
        return true;
      } else {
        toast.error('Failed to configure OpenAI API key');
        return false;
      }
    } catch (error) {
      console.error('Error configuring OpenAI API key:', error);
      toast.error('An error occurred while configuring OpenAI API key');
      return false;
    }
  }
}

export const setupService = new SetupService();
