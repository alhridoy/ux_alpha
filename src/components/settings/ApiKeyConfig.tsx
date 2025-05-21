
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { backendService } from '@/services/backendService';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useQuery } from '@tanstack/react-query';

const ApiKeyConfig = () => {
  const [apiKey, setApiKey] = useState<string>('');
  const [provider, setProvider] = useState<string>('openai');
  const [model, setModel] = useState<string>('gpt-4o');
  const [isSaving, setIsSaving] = useState<boolean>(false);
  
  // Query to get configured LLM providers
  const { data: configuredProviders, refetch } = useQuery({
    queryKey: ['configuredProviders'],
    queryFn: async () => {
      return await backendService.getConfiguredProviders();
    }
  });
  
  const isProviderConfigured = configuredProviders?.includes(provider);
  
  const handleSaveKey = async () => {
    if (!apiKey.trim()) {
      toast.error('Please enter a valid API key');
      return;
    }
    
    setIsSaving(true);
    
    try {
      // Send API key to backend using the backendService
      const success = await backendService.setApiKey(provider, apiKey, model);
      
      if (success) {
        toast.success(`${provider.toUpperCase()} API key saved successfully`);
        setApiKey(''); // Clear the input field for security
        refetch(); // Refresh the list of configured providers
      } else {
        toast.error(`Failed to save ${provider.toUpperCase()} API key`);
      }
    } catch (error) {
      console.error('Error saving API key:', error);
      toast.error('An error occurred while saving the API key');
    } finally {
      setIsSaving(false);
    }
  };
  
  const openAIModels = [
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  ];
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>LLM API Configuration</CardTitle>
        <CardDescription>
          Enter your API key to enable real AI-powered simulations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Provider</label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger>
                <SelectValue placeholder="Select LLM Provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openai">OpenAI</SelectItem>
                <SelectItem value="anthropic">Anthropic</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {provider === 'openai' && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Model</label>
              <Select value={model} onValueChange={setModel}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Model" />
                </SelectTrigger>
                <SelectContent>
                  {openAIModels.map(model => (
                    <SelectItem key={model.value} value={model.value}>{model.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          
          <div className="space-y-2">
            <Input
              type="password"
              placeholder={`Enter your ${provider} API key`}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Your API key is sent securely to the backend server.
            </p>
          </div>
          
          {isProviderConfigured && (
            <div className="p-2 bg-green-50 text-green-700 rounded-md text-sm">
              ✓ {provider.toUpperCase()} API key is configured
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={() => setApiKey('')} disabled={isSaving}>
          Clear
        </Button>
        <Button onClick={handleSaveKey} disabled={isSaving || !apiKey.trim()}>
          {isSaving ? 'Saving...' : 'Save API Key'}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ApiKeyConfig;
