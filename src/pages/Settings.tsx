
import React, { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Laptop, Server } from 'lucide-react';
import ApiKeyConfig from '@/components/settings/ApiKeyConfig';
import { toast } from 'sonner';
import { backendService } from '@/services/backendService';
import { useQuery } from '@tanstack/react-query';

const Settings = () => {
  const [stagehandApiKey, setStagehandApiKey] = useState<string>('');
  const [automationType, setAutomationType] = useState<'selenium' | 'stagehand'>('selenium');
  const [isSaving, setIsSaving] = useState<boolean>(false);
  
  // Query to get current browser automation type
  const { data: browserAutomationType, isLoading: isLoadingAutomationType, refetch: refetchAutomationType } = useQuery({
    queryKey: ['browserAutomationType'],
    queryFn: async () => {
      return await backendService.getBrowserAutomationType();
    }
  });
  
  // Query to check if Stagehand is configured
  const { data: isStagehandConfigured, isLoading: isCheckingStagehand, refetch: refetchStagehand } = useQuery({
    queryKey: ['stagehandConfig'],
    queryFn: async () => {
      return await backendService.isStagehandConfigured();
    }
  });
  
  // Update local state when data loads
  useEffect(() => {
    if (browserAutomationType) {
      setAutomationType(browserAutomationType);
    }
  }, [browserAutomationType]);
  
  const handleAutomationTypeChange = async (type: 'selenium' | 'stagehand') => {
    setIsSaving(true);
    
    try {
      const success = await backendService.configureBrowserAutomation(type);
      
      if (success) {
        setAutomationType(type);
        toast.success(`Browser automation set to ${type}`);
        refetchAutomationType();
      } else {
        toast.error('Failed to update browser automation type');
      }
    } catch (error) {
      console.error('Error configuring browser automation:', error);
      toast.error('An error occurred while configuring browser automation');
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleSaveStagehandKey = async () => {
    if (!stagehandApiKey.trim()) {
      toast.error('Please enter a valid Stagehand API key');
      return;
    }
    
    setIsSaving(true);
    
    try {
      const success = await backendService.setStagehandApiKey(stagehandApiKey);
      
      if (success) {
        toast.success('Stagehand API key saved successfully');
        setStagehandApiKey(''); // Clear for security
        refetchStagehand();
      } else {
        toast.error('Failed to save Stagehand API key');
      }
    } catch (error) {
      console.error('Error saving Stagehand API key:', error);
      toast.error('An error occurred while saving the Stagehand API key');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Layout>
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Configure UXAgent to connect with external services
          </p>
        </div>
        
        <Tabs defaultValue="api-keys">
          <TabsList className="mb-6">
            <TabsTrigger value="api-keys">API Keys</TabsTrigger>
            <TabsTrigger value="automation">Browser Automation</TabsTrigger>
          </TabsList>
          
          <TabsContent value="api-keys">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ApiKeyConfig />
              
              {automationType === 'stagehand' && (
                <Card>
                  <CardHeader>
                    <CardTitle>Stagehand Configuration</CardTitle>
                    <CardDescription>
                      Configure Stagehand for cloud-based browser automation
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Input
                          type="password"
                          placeholder="Enter your Stagehand API key"
                          value={stagehandApiKey}
                          onChange={(e) => setStagehandApiKey(e.target.value)}
                        />
                        <p className="text-xs text-muted-foreground">
                          Get your API key from stagehand.dev
                        </p>
                      </div>
                      
                      {isStagehandConfigured && (
                        <div className="p-2 bg-green-50 text-green-700 rounded-md text-sm">
                          ✓ Stagehand API key is configured
                        </div>
                      )}
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" onClick={() => setStagehandApiKey('')} disabled={isSaving}>
                      Clear
                    </Button>
                    <Button onClick={handleSaveStagehandKey} disabled={isSaving || !stagehandApiKey.trim()}>
                      {isSaving ? 'Saving...' : 'Save API Key'}
                    </Button>
                  </CardFooter>
                </Card>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="automation">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Laptop className="h-5 w-5 text-uxagent-purple" />
                    <CardTitle>Browser Automation</CardTitle>
                  </div>
                  <CardDescription>
                    Configure browser automation for UX testing
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-col space-y-4">
                    <label className="text-sm font-medium">Automation Type</label>
                    <div className="flex gap-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          id="selenium"
                          name="automationType"
                          checked={automationType === 'selenium'}
                          onChange={() => handleAutomationTypeChange('selenium')}
                          className="rounded text-uxagent-purple"
                        />
                        <Label htmlFor="selenium">Selenium (Local)</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          id="stagehand"
                          name="automationType"
                          checked={automationType === 'stagehand'}
                          onChange={() => handleAutomationTypeChange('stagehand')}
                          className="rounded text-uxagent-purple"
                        />
                        <Label htmlFor="stagehand">Stagehand (Cloud)</Label>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <p className="text-sm text-muted-foreground">
                    {automationType === 'selenium' 
                      ? 'Selenium requires Chrome/Firefox and WebDriver to be installed locally.' 
                      : 'Stagehand offers cloud-based browser automation without local setup.'}
                  </p>
                </CardFooter>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Settings;
