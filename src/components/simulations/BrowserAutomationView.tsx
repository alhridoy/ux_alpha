
import React, { useState, useEffect } from 'react';
import { AgentAction } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronUp, ChevronDown, PlayCircle, Laptop, ExternalLink, Key } from 'lucide-react';
import { toast } from 'sonner';
import { backendService } from '@/services/backendService';
import { stagehandConnector } from '@/services/stagehandConnector';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import LiveBrowserView from './LiveBrowserView';

interface BrowserAutomationViewProps {
  actions: AgentAction[];
  webUrl: string;
  simulationId?: string;
  isLiveSimulation?: boolean;
}

const BrowserAutomationView: React.FC<BrowserAutomationViewProps> = ({
  actions,
  webUrl,
  simulationId = '',
  isLiveSimulation = false
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isConfiguring, setIsConfiguring] = useState(false);
  const [isStagehandConfigured, setIsStagehandConfigured] = useState(false);
  const [isApiKeyDialogOpen, setIsApiKeyDialogOpen] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [isSubmittingKey, setIsSubmittingKey] = useState(false);

  useEffect(() => {
    // Check if Stagehand is configured
    const checkStagehandConfig = async () => {
      try {
        const stagehandConfigured = await stagehandConnector.isConfigured();
        setIsStagehandConfigured(stagehandConfigured);
      } catch (error) {
        console.error('Error checking Stagehand configuration:', error);
      }
    };

    checkStagehandConfig();
  }, []);

  const handleApiKeySubmit = async () => {
    if (!apiKey.trim()) {
      toast.error('Please enter a valid API key');
      return;
    }

    setIsSubmittingKey(true);

    try {
      // Use the stagehandConnector to configure the API key
      const success = await stagehandConnector.configure(apiKey);

      if (success) {
        setIsStagehandConfigured(true);
        setIsApiKeyDialogOpen(false);
        toast.success('Stagehand API key configured successfully');
      }
    } catch (error) {
      console.error('Error configuring Stagehand API key:', error);
      toast.error('An error occurred while configuring Stagehand');
    } finally {
      setIsSubmittingKey(false);
      setApiKey('');
    }
  };

  // Helper function to describe action type
  const getActionTypeDescription = (action: AgentAction) => {
    switch (action.type) {
      case 'click':
        return 'Click';
      case 'input':
        return 'Type text';
      case 'scroll':
        return 'Scroll';
      case 'navigate':
        return 'Navigate';
      case 'wait':
        return 'Wait';
      default:
        return action.type;
    }
  };

  return (
    <>
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Laptop className="h-5 w-5 text-uxagent-purple" />
              <CardTitle>Browser Automation</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-sm font-medium text-uxagent-purple">
                Using Stagehand AI
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="text-sm text-uxagent-purple hover:text-uxagent-dark-purple hover:bg-uxagent-light-purple/20"
              >
                {isCollapsed ? (
                  <>
                    <ChevronDown className="h-4 w-4 mr-1" />
                    Expand
                  </>
                ) : (
                  <>
                    <ChevronUp className="h-4 w-4 mr-1" />
                    Collapse
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>

        {!isCollapsed && (
          <CardContent>
            <div className="bg-slate-50 border rounded-md p-4 mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="h-3 w-3 rounded-full bg-red-500"></div>
                    <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
                    <div className="h-3 w-3 rounded-full bg-green-500"></div>
                  </div>
                  <span className="text-sm font-medium truncate max-w-[300px]">
                    {webUrl}
                  </span>
                </div>
                <Button variant="outline" size="sm" className="h-7">
                  <PlayCircle className="h-4 w-4 mr-1" />
                  <span className="text-xs">Open Full Trace Player</span>
                </Button>
              </div>
              <LiveBrowserView
                simulationId={simulationId}
                isActive={isLiveSimulation || simulationId !== ''}
              />

              <div className="mt-3 text-center">
                <p className="text-xs text-uxagent-purple mb-1">
                  Stagehand uses its own AI to handle browser interactions
                </p>
                <a
                  href="https://docs.stagehand.dev"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs flex items-center justify-center gap-1 text-uxagent-purple hover:underline"
                >
                  Learn more about Stagehand
                  <ExternalLink className="h-3 w-3" />
                </a>
                {!isStagehandConfigured && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsApiKeyDialogOpen(true)}
                    className="mt-2"
                  >
                    <Key className="h-3 w-3 mr-1" />
                    Configure Stagehand API Key
                  </Button>
                )}
              </div>
            </div>

            <div className="bg-white border rounded-md">
              <div className="flex justify-between items-center p-3 border-b">
                <h3 className="font-semibold">Action Log</h3>
                <div className="text-xs text-muted-foreground">
                  Using Stagehand observe + act pattern
                </div>
              </div>
              <div className="p-3 space-y-3 max-h-[300px] overflow-y-auto">
                {actions.map((action, index) => (
                  <div
                    key={action.id}
                    className="p-3 rounded-md bg-slate-50 border"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-uxagent-light-purple flex items-center justify-center text-uxagent-purple font-medium text-xs">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm">
                          <span className="font-medium">Step {index + 1}:</span> {action.reasoning}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Action: <span className="font-medium">{getActionTypeDescription(action)}</span>
                          {action.target && <> on <span className="font-mono">{action.target}</span></>}
                        </p>
                        {action.value && action.type === "input" && (
                          <p className="text-xs text-gray-500 mt-1">
                            Input: <span className="font-mono">{action.value}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {actions.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No actions recorded for this simulation yet
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      <Dialog open={isApiKeyDialogOpen} onOpenChange={setIsApiKeyDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Configure Stagehand API Key</DialogTitle>
            <DialogDescription>
              Enter your Stagehand API key to enable AI-powered browser automation.
              You can get an API key from <a href="https://stagehand.dev" target="_blank" rel="noopener noreferrer" className="text-uxagent-purple hover:underline">stagehand.dev</a>
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Input
              placeholder="sk-stagehand-xxxxxxxxxxx"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="font-mono"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Stagehand is an advanced tool for browser automation that uses AI to interact with web pages in a more natural way.
            </p>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsApiKeyDialogOpen(false)} disabled={isSubmittingKey}>
              Cancel
            </Button>
            <Button onClick={handleApiKeySubmit} disabled={isSubmittingKey}>
              {isSubmittingKey ? 'Configuring...' : 'Save API Key'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default BrowserAutomationView;
