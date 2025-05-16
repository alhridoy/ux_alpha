
import React, { useState } from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageSquare, Search, ArrowUpRight, Plus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { sampleInterviews, sampleSimulations } from '@/data/sampleData';
import { Interview } from '@/types';

const Interviews = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInterview, setSelectedInterview] = useState<Interview | null>(sampleInterviews[0]);
  
  const filteredInterviews = sampleInterviews.filter((interview) => {
    const simulation = sampleSimulations.find(sim => sim.id === interview.simulationId);
    if (!simulation) return false;
    
    return (
      simulation.persona.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      simulation.task.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });
  
  return (
    <Layout>
      <div className="animate-fade-in">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">Agent Interviews</h1>
            <p className="text-muted-foreground">
              Post-test interviews with AI personas for deeper insights
            </p>
          </div>
          <Button className="bg-uxagent-purple hover:bg-uxagent-dark-purple">
            <MessageSquare className="h-4 w-4 mr-2" />
            New Interview
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Interview Library</CardTitle>
                <CardDescription>Select an interview to view details</CardDescription>
                <div className="relative mt-2">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input 
                    placeholder="Search interviews..." 
                    className="pl-8"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)} 
                  />
                </div>
              </CardHeader>
              <CardContent className="max-h-[500px] overflow-y-auto">
                <div className="space-y-3">
                  {filteredInterviews.length === 0 ? (
                    <p className="text-center p-4 text-muted-foreground text-sm">
                      No interviews match your search
                    </p>
                  ) : (
                    filteredInterviews.map((interview) => {
                      const simulation = sampleSimulations.find(sim => sim.id === interview.simulationId);
                      if (!simulation) return null;
                      
                      return (
                        <div 
                          key={interview.id}
                          className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${selectedInterview?.id === interview.id ? 'bg-uxagent-light-purple' : 'hover:bg-muted'}`}
                          onClick={() => setSelectedInterview(interview)}
                        >
                          <div className="h-10 w-10 rounded-full overflow-hidden flex-shrink-0 mr-3">
                            <img 
                              src={`${simulation.persona.profileImage}?w=80&h=80&fit=crop&crop=faces&auto=format`} 
                              alt={simulation.persona.name}
                              className="h-full w-full object-cover" 
                            />
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-sm">{simulation.persona.name}</p>
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">{simulation.task}</p>
                            <p className="text-xs text-muted-foreground">
                              {interview.questions.length} questions
                            </p>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="lg:col-span-2">
            {selectedInterview ? (
              <Card className="animate-fade-in">
                <CardHeader>
                  {(() => {
                    const simulation = sampleSimulations.find(sim => sim.id === selectedInterview.simulationId);
                    if (!simulation) return null;
                    
                    return (
                      <>
                        <div className="flex items-center justify-between mb-2">
                          <CardTitle className="flex items-center">
                            <MessageSquare className="h-5 w-5 mr-2 text-uxagent-purple" />
                            <span>Interview Transcript</span>
                          </CardTitle>
                          <Button variant="ghost" size="sm" className="text-uxagent-purple">
                            View Simulation
                            <ArrowUpRight className="h-4 w-4 ml-1" />
                          </Button>
                        </div>
                        <CardDescription className="flex items-center">
                          <div className="h-6 w-6 rounded-full overflow-hidden mr-2">
                            <img 
                              src={`${simulation.persona.profileImage}?w=48&h=48&fit=crop&crop=faces&auto=format`} 
                              alt={simulation.persona.name}
                              className="h-full w-full object-cover" 
                            />
                          </div>
                          <span>
                            Interview with {simulation.persona.name} • {simulation.persona.age}, {simulation.persona.occupation}
                          </span>
                        </CardDescription>
                        <p className="text-sm mt-1">{simulation.task}</p>
                      </>
                    );
                  })()}
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-6">
                    {selectedInterview.questions.map((item, index) => (
                      <div key={index} className="space-y-3">
                        <div className="flex">
                          <div className="w-8 h-8 rounded-full bg-uxagent-dark-purple flex items-center justify-center mr-3 flex-shrink-0">
                            <span className="text-white text-xs font-medium">UX</span>
                          </div>
                          <div className="bg-uxagent-soft-gray rounded-lg p-3 rounded-tl-none flex-1">
                            <p className="text-sm font-medium">{item.question}</p>
                          </div>
                        </div>
                        
                        <div className="flex">
                          <div className="w-8 h-8 rounded-full bg-white border border-uxagent-purple flex items-center justify-center mr-3 flex-shrink-0">
                            <span className="text-uxagent-purple text-xs font-medium">AI</span>
                          </div>
                          <div className="bg-white border rounded-lg p-3 rounded-tl-none flex-1">
                            <p className="text-sm">{item.answer}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="relative mt-6">
                    <div className="flex items-center">
                      <Input 
                        placeholder="Ask a follow-up question..." 
                        className="pr-24"
                      />
                      <Button className="absolute right-0 bg-uxagent-purple hover:bg-uxagent-dark-purple">
                        Ask
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="h-full flex flex-col items-center justify-center p-8 bg-white rounded-lg border border-dashed">
                <div className="w-16 h-16 bg-uxagent-light-purple rounded-full flex items-center justify-center mb-4">
                  <MessageSquare className="h-8 w-8 text-uxagent-purple" />
                </div>
                <h3 className="text-lg font-medium mb-1">Select an Interview</h3>
                <p className="text-muted-foreground text-center max-w-md mb-4">
                  Choose an interview from the library or create a new one
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Start New Interview
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Interviews;
