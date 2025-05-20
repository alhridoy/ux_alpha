
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { llmService } from '@/services/llmService';

const ApiKeyConfig = () => {
  const [apiKey, setApiKey] = useState<string>('');
  const [isSaved, setIsSaved] = useState<boolean>(false);
  
  // Check if API key is stored in localStorage
  useEffect(() => {
    const storedKey = localStorage.getItem('llm_api_key');
    if (storedKey) {
      setApiKey(storedKey);
      llmService.setApiKey(storedKey);
      setIsSaved(true);
    }
  }, []);
  
  const handleSaveKey = () => {
    if (!apiKey.trim()) {
      toast.error('Please enter a valid API key');
      return;
    }
    
    // Save to localStorage (in a real-world app, this should be more secure)
    localStorage.setItem('llm_api_key', apiKey);
    
    // Configure the LLM service
    llmService.setApiKey(apiKey);
    
    setIsSaved(true);
    toast.success('API key saved successfully');
  };
  
  const handleClearKey = () => {
    localStorage.removeItem('llm_api_key');
    setApiKey('');
    setIsSaved(false);
    toast.info('API key removed');
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>LLM API Configuration</CardTitle>
        <CardDescription>
          Enter your OpenAI API key to enable real AI-powered simulations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Input
              type="password"
              placeholder="sk-..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Your API key is stored locally in your browser.
            </p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={handleClearKey}>
          Clear Key
        </Button>
        <Button onClick={handleSaveKey}>
          Save API Key
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ApiKeyConfig;
