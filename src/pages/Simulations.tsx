
import React, { useState } from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tab, Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { CheckCircle2, XCircle, Clock, MousePointerClick, Keyboard, ArrowRight, Brain, Download, Play } from 'lucide-react';
import { sampleSimulations } from '@/data/sampleData';
import { SimulationResult } from '@/types';

const Simulations = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [selectedSimulation, setSelectedSimulation] = useState<SimulationResult | null>(sampleSimulations[0]);

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  
  return (
    <Layout>
      <div className="animate-fade-in">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">Simulations</h1>
            <p className="text-muted-foreground">
              View and analyze usability test simulations
            </p>
          </div>
          <Button className="bg-uxagent-purple hover:bg-uxagent-dark-purple">
            <Play className="h-4 w-4 mr-2" />
            New Simulation
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Simulation History</CardTitle>
                <CardDescription>Select a simulation to analyze</CardDescription>
              </CardHeader>
              <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
                <div className="px-4">
                  <TabsList className="w-full">
                    <TabsTrigger value="all" className="flex-1">All</TabsTrigger>
                    <TabsTrigger value="completed" className="flex-1">Completed</TabsTrigger>
                    <TabsTrigger value="failed" className="flex-1">Failed</TabsTrigger>
                  </TabsList>
                </div>
                
                <TabsContent value="all">
                  <CardContent className="max-h-[500px] overflow-y-auto">
                    <div className="space-y-3">
                      {sampleSimulations.map((simulation) => (
                        <SimulationListItem 
                          key={simulation.id}
                          simulation={simulation} 
                          isSelected={selectedSimulation?.id === simulation.id}
                          onClick={() => setSelectedSimulation(simulation)}
                        />
                      ))}
                    </div>
                  </CardContent>
                </TabsContent>
                
                <TabsContent value="completed">
                  <CardContent className="max-h-[500px] overflow-y-auto">
                    <div className="space-y-3">
                      {sampleSimulations
                        .filter(sim => sim.taskCompleted)
                        .map((simulation) => (
                          <SimulationListItem 
                            key={simulation.id}
                            simulation={simulation} 
                            isSelected={selectedSimulation?.id === simulation.id}
                            onClick={() => setSelectedSimulation(simulation)}
                          />
                        ))}
                    </div>
                  </CardContent>
                </TabsContent>
                
                <TabsContent value="failed">
                  <CardContent className="max-h-[500px] overflow-y-auto">
                    <div className="space-y-3">
                      {sampleSimulations
                        .filter(sim => !sim.taskCompleted)
                        .map((simulation) => (
                          <SimulationListItem 
                            key={simulation.id}
                            simulation={simulation} 
                            isSelected={selectedSimulation?.id === simulation.id}
                            onClick={() => setSelectedSimulation(simulation)}
                          />
                        ))}
                    </div>
                  </CardContent>
                </TabsContent>
              </Tabs>
            </Card>
          </div>
          
          <div className="lg:col-span-2">
            {selectedSimulation && (
              <Card className="animate-fade-in">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center mb-2">
                        {selectedSimulation.taskCompleted ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500 mr-2" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500 mr-2" />
                        )}
                        <CardTitle className="text-xl">
                          {selectedSimulation.taskCompleted ? 'Task Completed' : 'Task Failed'}
                        </CardTitle>
                      </div>
                      <CardDescription className="text-base">{selectedSimulation.task}</CardDescription>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center justify-end mb-1">
                        <Clock className="h-4 w-4 text-muted-foreground mr-1" />
                        <span className="text-sm font-medium">{formatDuration(selectedSimulation.durationSeconds)}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {new Date(selectedSimulation.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  <div className="flex items-center p-3 bg-muted rounded-lg">
                    <div className="h-12 w-12 rounded-full overflow-hidden mr-3">
                      <img 
                        src={`${selectedSimulation.persona.profileImage}?w=96&h=96&fit=crop&crop=faces&auto=format`} 
                        alt={selectedSimulation.persona.name}
                        className="h-full w-full object-cover" 
                      />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{selectedSimulation.persona.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {selectedSimulation.persona.age}, {selectedSimulation.persona.gender} • {selectedSimulation.persona.occupation}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">View Profile</Button>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-3 text-sm text-muted-foreground">ACTIONS</h3>
                    <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                      {selectedSimulation.actions.map((action, index) => (
                        <div key={action.id} className="flex">
                          <div className="mr-3 flex flex-col items-center">
                            <div className="h-8 w-8 rounded-full bg-uxagent-light-purple flex items-center justify-center">
                              {action.type === 'click' && <MousePointerClick className="h-4 w-4 text-uxagent-purple" />}
                              {action.type === 'input' && <Keyboard className="h-4 w-4 text-uxagent-purple" />}
                              {(action.type !== 'click' && action.type !== 'input') && <ArrowRight className="h-4 w-4 text-uxagent-purple" />}
                            </div>
                            {index < selectedSimulation.actions.length - 1 && (
                              <div className="w-0.5 h-full bg-uxagent-light-purple"></div>
                            )}
                          </div>
                          <div className="bg-white rounded-lg border p-3 mb-2 flex-1">
                            <div className="flex justify-between items-center mb-1">
                              <p className="font-medium text-sm">
                                {action.type.charAt(0).toUpperCase() + action.type.slice(1)}: {action.target}
                              </p>
                              <span className="text-xs text-muted-foreground">
                                {new Date(action.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                            {action.value && (
                              <p className="text-sm text-muted-foreground mb-2">Value: {action.value}</p>
                            )}
                            <div className="flex items-start mt-2">
                              <Brain className="h-4 w-4 text-uxagent-purple mr-2 mt-0.5" />
                              <p className="text-sm">{action.reasoning}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h3 className="font-semibold mb-2 text-sm text-muted-foreground">REFLECTIONS</h3>
                      <ul className="list-disc pl-5 space-y-2">
                        {selectedSimulation.reflections.map((reflection, index) => (
                          <li key={index} className="text-sm">{reflection}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2 text-sm text-muted-foreground">WONDERINGS</h3>
                      <ul className="list-disc pl-5 space-y-2">
                        {selectedSimulation.wonderings.map((wondering, index) => (
                          <li key={index} className="text-sm">{wondering}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button className="bg-uxagent-purple hover:bg-uxagent-dark-purple sm:flex-1">
                      Interview Agent
                    </Button>
                    <Button variant="outline" className="sm:flex-1">
                      <Download className="h-4 w-4 mr-2" />
                      Export Report
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

interface SimulationListItemProps {
  simulation: SimulationResult;
  isSelected: boolean;
  onClick: () => void;
}

const SimulationListItem: React.FC<SimulationListItemProps> = ({ simulation, isSelected, onClick }) => {
  return (
    <div 
      className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${isSelected ? 'bg-uxagent-light-purple' : 'hover:bg-muted'}`}
      onClick={onClick}
    >
      <div className="h-10 w-10 rounded-full overflow-hidden flex-shrink-0 mr-3">
        <img 
          src={`${simulation.persona.profileImage}?w=80&h=80&fit=crop&crop=faces&auto=format`} 
          alt={simulation.persona.name}
          className="h-full w-full object-cover" 
        />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between">
          <p className="font-medium text-sm truncate max-w-[150px]">{simulation.persona.name}</p>
          <span className={`text-xs px-1.5 py-0.5 rounded-full ${simulation.taskCompleted ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {simulation.taskCompleted ? 'Success' : 'Failed'}
          </span>
        </div>
        <p className="text-xs text-muted-foreground truncate max-w-[200px]">{simulation.task}</p>
        <p className="text-xs text-muted-foreground">
          {new Date(simulation.timestamp).toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default Simulations;
