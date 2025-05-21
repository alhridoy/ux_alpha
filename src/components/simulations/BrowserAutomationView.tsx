
import React, { useState } from 'react';
import { AgentAction } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronUp, ChevronDown, PlayCircle, Laptop, ExternalLink } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { backendService } from '@/services/backendService';

interface BrowserAutomationViewProps {
  actions: AgentAction[];
  webUrl: string;
}

const BrowserAutomationView: React.FC<BrowserAutomationViewProps> = ({ actions, webUrl }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [automationType, setAutomationType] = useState<'selenium' | 'stagehand'>('selenium');
  const [isConfiguring, setIsConfiguring] = useState(false);

  React.useEffect(() => {
    // Get the current browser automation type when component mounts
    const getBrowserType = async () => {
      const type = await backendService.getBrowserAutomationType();
      if (type) {
        setAutomationType(type);
      }
    };
    
    getBrowserType();
  }, []);

  const handleAutomationTypeChange = async (value: string) => {
    if (value !== 'selenium' && value !== 'stagehand') return;
    
    setIsConfiguring(true);
    
    try {
      const success = await backendService.configureBrowserAutomation(value);
      
      if (success) {
        setAutomationType(value);
        toast.success(`Browser automation set to ${value}`);
      } else {
        toast.error(`Failed to set browser automation to ${value}`);
      }
    } catch (error) {
      console.error('Error setting browser automation:', error);
      toast.error('An error occurred while configuring browser automation');
    } finally {
      setIsConfiguring(false);
    }
  };

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Laptop className="h-5 w-5 text-uxagent-purple" />
            <CardTitle>Browser Automation</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Select
              value={automationType}
              onValueChange={handleAutomationTypeChange}
              disabled={isConfiguring}
            >
              <SelectTrigger className="w-[160px] h-8">
                <SelectValue placeholder="Select engine" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="selenium">Selenium</SelectItem>
                <SelectItem value="stagehand">Stagehand (AI)</SelectItem>
              </SelectContent>
            </Select>
            
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
            <div className="bg-white border rounded-md h-[250px] flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Laptop className="h-12 w-12 mx-auto mb-2 text-muted-foreground/50" />
                <p>Browser view will appear here during live simulations</p>
                <p className="text-sm">Using {automationType === 'stagehand' ? 'Stagehand (AI-powered)' : 'Selenium'} for automation</p>
                {automationType === 'stagehand' && (
                  <div className="mt-3">
                    <a 
                      href="https://docs.stagehand.dev" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs flex items-center justify-center gap-1 text-uxagent-purple hover:underline"
                    >
                      Learn more about Stagehand
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white border rounded-md">
            <div className="flex justify-between items-center p-3 border-b">
              <h3 className="font-semibold">Action Log</h3>
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
                      {action.target && (
                        <p className="text-xs text-gray-500 mt-1">
                          Target: <span className="font-mono">{action.target}</span>
                        </p>
                      )}
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
  );
};

export default BrowserAutomationView;
