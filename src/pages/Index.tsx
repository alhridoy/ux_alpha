
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowUpRight, BarChart3, UserRound, GanttChartSquare, MessageSquare, Plus } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import { samplePersonas, sampleSimulations, sampleInterviews } from '@/data/sampleData';

const Index = () => {
  const navigate = useNavigate();
  
  return (
    <Layout>
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">UXAgent Dashboard</h1>
          <p className="text-muted-foreground">
            Simulate usability testing with diverse AI personas to get early feedback on your designs.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Personas"
            value={samplePersonas.length}
            icon={<UserRound className="h-4 w-4" />}
            description="Virtual users"
            onClick={() => navigate('/personas')}
          />
          <StatCard
            title="Simulations"
            value={sampleSimulations.length}
            icon={<GanttChartSquare className="h-4 w-4" />}
            description="Completed tests"
            onClick={() => navigate('/simulations')}
          />
          <StatCard
            title="Interviews"
            value={sampleInterviews.length}
            icon={<MessageSquare className="h-4 w-4" />}
            description="Follow-up insights"
            onClick={() => navigate('/interviews')}
          />
          <StatCard
            title="Issues Found"
            value={7}
            icon={<BarChart3 className="h-4 w-4" />}
            description="Potential improvements"
            onClick={() => {}}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Recent Simulations</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-uxagent-purple hover:text-uxagent-dark-purple"
                  onClick={() => navigate('/simulations')}
                >
                  View all
                  <ArrowUpRight className="h-4 w-4 ml-1" />
                </Button>
              </CardTitle>
              <CardDescription>Latest usability tests run by AI agents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {sampleSimulations.map((simulation) => (
                  <div key={simulation.id} className="flex items-center p-3 rounded-lg hover:bg-muted transition-colors">
                    <div className="h-10 w-10 rounded-full bg-uxagent-light-purple flex items-center justify-center mr-3 flex-shrink-0">
                      <GanttChartSquare className="h-5 w-5 text-uxagent-purple" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">{simulation.task}</p>
                        <span className={`text-xs px-2 py-1 rounded-full ${simulation.taskCompleted ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
                          {simulation.taskCompleted ? 'Completed' : 'Failed'}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {simulation.persona.name} • {new Date(simulation.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full bg-uxagent-purple hover:bg-uxagent-dark-purple" onClick={() => navigate('/simulations/new')}>
                <Plus className="h-4 w-4 mr-2" />
                New Simulation
              </Button>
            </CardFooter>
          </Card>
          
          <Card className="animate-slide-up [animation-delay:150ms]">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Available Personas</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-uxagent-purple hover:text-uxagent-dark-purple"
                  onClick={() => navigate('/personas')}
                >
                  View all
                  <ArrowUpRight className="h-4 w-4 ml-1" />
                </Button>
              </CardTitle>
              <CardDescription>Virtual users with diverse backgrounds</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {samplePersonas.map((persona) => (
                  <div key={persona.id} className="flex items-center p-3 rounded-lg hover:bg-muted transition-colors">
                    <div className="h-10 w-10 rounded-full overflow-hidden mr-3 flex-shrink-0">
                      <img 
                        src={`${persona.profileImage}?w=80&h=80&fit=crop&crop=faces&auto=format`} 
                        alt={persona.name} 
                        className="h-full w-full object-cover"
                      />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{persona.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {persona.age}, {persona.occupation} • {persona.techExperience} tech user
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full bg-uxagent-purple hover:bg-uxagent-dark-purple" onClick={() => navigate('/personas/new')}>
                <Plus className="h-4 w-4 mr-2" />
                New Persona
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  description: string;
  onClick: () => void;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, description, onClick }) => {
  return (
    <Card className="animate-slide-up cursor-pointer hover:border-uxagent-purple transition-colors" onClick={onClick}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
          {icon}
          <span className="ml-1">{title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
      </CardContent>
    </Card>
  );
};

export default Index;
