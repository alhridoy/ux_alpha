
import React from 'react';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  MousePointer, 
  Keyboard, 
  ArrowDownUp, 
  Globe, 
  FileQuestion, 
  BrainCircuit,
  Eye,
  PauseCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SimulationResult, AgentAction } from '@/types';
import { formatDistanceToNow } from 'date-fns';

type SimulationDetailProps = {
  simulation: SimulationResult;
  onBack: () => void;
};

const SimulationDetail = ({ simulation, onBack }: SimulationDetailProps) => {
  const formattedTime = formatDistanceToNow(simulation.timestamp, { addSuffix: true });
  
  // Helper to get the appropriate icon for each action type
  const getActionIcon = (type: string) => {
    switch (type) {
      case 'click':
        return <MousePointer className="h-4 w-4" />;
      case 'input':
        return <Keyboard className="h-4 w-4" />;
      case 'scroll':
        return <ArrowDownUp className="h-4 w-4" />;
      case 'hover':
        return <Eye className="h-4 w-4" />;
      case 'navigate':
        return <Globe className="h-4 w-4" />;
      case 'wait':
        return <PauseCircle className="h-4 w-4" />;
      case 'error':
        return <FileQuestion className="h-4 w-4" />;
      default:
        return <MousePointer className="h-4 w-4" />;
    }
  };

  // Format timestamp to readable time
  const formatTimestamp = (timestamp: number): string => {
    const seconds = Math.round((timestamp - simulation.actions[0].timestamp) / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };
  
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={onBack}>
          Back to simulations
        </Button>
        <Button variant="outline">
          Export Results
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl">Simulation Report</CardTitle>
                <Badge variant={simulation.taskCompleted ? "success" : "destructive"} className="text-sm">
                  {simulation.taskCompleted ? (
                    <CheckCircle className="h-3.5 w-3.5 mr-1" />
                  ) : (
                    <XCircle className="h-3.5 w-3.5 mr-1" />
                  )}
                  {simulation.taskCompleted ? "Task Completed" : "Task Incomplete"}
                </Badge>
              </div>
              <CardDescription>
                <div className="flex items-center mt-1">
                  <Clock className="h-4 w-4 mr-1 text-muted-foreground" />
                  <span className="mr-3">{simulation.durationSeconds} seconds</span>
                  <span className="text-muted-foreground">•</span>
                  <span className="ml-3">{simulation.actions.length} actions</span>
                  <span className="text-muted-foreground mx-2">•</span>
                  <span>{formattedTime}</span>
                </div>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <h3 className="font-medium text-sm text-muted-foreground mb-2">TASK</h3>
                <p className="text-base">"{simulation.task}"</p>
              </div>
              
              <div className="mb-6">
                <h3 className="font-medium text-sm text-muted-foreground mb-2">WEBSITE</h3>
                <div className="flex items-center">
                  <Globe className="h-4 w-4 mr-2 text-uxagent-purple" />
                  <a 
                    href={simulation.webUrl} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-uxagent-purple hover:underline"
                  >
                    {new URL(simulation.webUrl).hostname}
                  </a>
                </div>
              </div>
              
              <Tabs defaultValue="actions" className="w-full">
                <TabsList>
                  <TabsTrigger value="actions">Action Trace</TabsTrigger>
                  <TabsTrigger value="reflections">Reflections</TabsTrigger>
                  <TabsTrigger value="wonderings">Wonderings</TabsTrigger>
                </TabsList>
                
                <TabsContent value="actions" className="pt-4">
                  <div className="space-y-4">
                    {simulation.actions.map((action, index) => (
                      <div key={action.id} className="relative pl-6 pb-6">
                        {/* Timeline connector */}
                        {index < simulation.actions.length - 1 && (
                          <div className="absolute left-[11px] top-[28px] bottom-0 w-0.5 bg-muted-foreground/20" />
                        )}
                        
                        <div className="flex items-start">
                          <div className="absolute left-0 bg-white p-1 rounded-full border border-muted">
                            {getActionIcon(action.type)}
                          </div>
                          <div className="ml-4">
                            <div className="flex items-center mb-1">
                              <Badge variant="outline" className="mr-2 capitalize">
                                {action.type}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {formatTimestamp(action.timestamp)}
                              </span>
                            </div>
                            {action.target && (
                              <p className="text-sm mb-1">
                                <span className="font-medium">Target:</span> {action.target}
                              </p>
                            )}
                            {action.value && (
                              <p className="text-sm mb-1">
                                <span className="font-medium">Value:</span> {action.value}
                              </p>
                            )}
                            <p className="text-sm text-muted-foreground">{action.reasoning}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
                
                <TabsContent value="reflections" className="pt-4">
                  <div className="space-y-4">
                    {simulation.reflections.map((reflection, index) => (
                      <div key={index} className="bg-slate-50 p-4 rounded-lg border">
                        <div className="flex items-center mb-2">
                          <BrainCircuit className="h-4 w-4 mr-2 text-uxagent-purple" />
                          <span className="font-medium">Reflection {index + 1}</span>
                        </div>
                        <p className="text-sm">{reflection}</p>
                      </div>
                    ))}
                  </div>
                </TabsContent>
                
                <TabsContent value="wonderings" className="pt-4">
                  <div className="space-y-4">
                    {simulation.wonderings.map((wondering, index) => (
                      <div key={index} className="bg-uxagent-light-purple/30 p-4 rounded-lg border border-uxagent-light-purple">
                        <div className="flex items-center mb-2">
                          <FileQuestion className="h-4 w-4 mr-2 text-uxagent-purple" />
                          <span className="font-medium">Wondering {index + 1}</span>
                        </div>
                        <p className="text-sm">{wondering}</p>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
        
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Persona Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center mb-4">
                <div className="h-20 w-20 rounded-full overflow-hidden mb-3">
                  <img 
                    src={`${simulation.persona.profileImage}?w=160&h=160&fit=crop&crop=faces&auto=format`}
                    alt={simulation.persona.name}
                    className="h-full w-full object-cover" 
                  />
                </div>
                <h3 className="text-lg font-medium">{simulation.persona.name}</h3>
                <p className="text-sm text-muted-foreground">
                  {simulation.persona.age} y/o, {simulation.persona.gender}
                </p>
                <p className="text-sm text-muted-foreground">
                  {simulation.persona.occupation}
                </p>
              </div>
              
              <Separator className="my-4" />
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2 text-sm text-muted-foreground">TECH EXPERIENCE</h3>
                  <Badge variant="outline" className="block w-full text-center py-1">
                    {simulation.persona.techExperience}
                  </Badge>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2 text-sm text-muted-foreground">TRAITS</h3>
                  <div className="flex flex-wrap gap-2">
                    {simulation.persona.traits.map((trait, index) => (
                      <Badge key={index} className="bg-uxagent-light-purple text-uxagent-dark-purple hover:bg-uxagent-light-purple">
                        {trait}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2 text-sm text-muted-foreground">GOALS</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {simulation.persona.goals.map((goal, index) => (
                      <li key={index} className="text-sm">{goal}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2 text-sm text-muted-foreground">PAIN POINTS</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {simulation.persona.painPoints.map((painPoint, index) => (
                      <li key={index} className="text-sm">{painPoint}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <Separator className="my-4" />
              
              <Button variant="outline" className="w-full">
                <MessageSquare className="h-4 w-4 mr-2" />
                Interview {simulation.persona.name.split(' ')[0]}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SimulationDetail;
