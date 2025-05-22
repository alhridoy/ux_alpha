
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, FilterX } from 'lucide-react';
import { Persona, SimulationResult } from '@/types';
import { toast } from 'sonner';
import SimulationCard from '@/components/simulations/SimulationCard';
import SimulationDetail from '@/components/simulations/SimulationDetail';
import NewSimulationModal from '@/components/simulations/NewSimulationModal';
import { runSimulation } from '@/services/agentService';
import { usePersonas } from '@/contexts/PersonasContext';

const Simulations = () => {
  const location = useLocation();
  const { personas } = usePersonas();
  const [simulations, setSimulations] = useState<SimulationResult[]>([]);
  const [isNewSimulationModalOpen, setIsNewSimulationModalOpen] = useState(false);
  const [selectedSimulation, setSelectedSimulation] = useState<SimulationResult | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Check if we have a selected persona from navigation
  useEffect(() => {
    const state = location.state as { selectedPersona?: Persona } | null;
    if (state?.selectedPersona) {
      // Open the new simulation modal with the selected persona
      setIsNewSimulationModalOpen(true);
      // Clear the location state to prevent reopening the modal on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  // Filter simulations based on search term and active tab
  const getFilteredSimulations = (status: 'active' | 'completed' | 'all') => {
    let filtered = simulations;

    // Apply search filter
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      filtered = filtered.filter(sim =>
        sim.task.toLowerCase().includes(lowerSearch) ||
        sim.persona.name.toLowerCase().includes(lowerSearch) ||
        new URL(sim.webUrl).hostname.toLowerCase().includes(lowerSearch)
      );
    }

    // Apply status filter
    if (status === 'active') {
      return filtered.filter(sim => !sim.taskCompleted);
    } else if (status === 'completed') {
      return filtered.filter(sim => sim.taskCompleted);
    }

    return filtered;
  };

  const handleCreateSimulation = async (simulation: SimulationResult) => {
    try {
      // In a real-world scenario, this would call an API to start the simulation
      // For now, we're using the mock implementation from our service
      const result = await runSimulation(
        simulation.persona,
        simulation.webUrl,
        simulation.task
      );

      setSimulations(prev => [result, ...prev]);
      toast.success("Simulation completed successfully");
    } catch (error) {
      console.error("Error creating simulation:", error);
      toast.error("Failed to create simulation");
    }
  };

  const handleClearSearch = () => {
    setSearchTerm('');
  };

  const renderSimulationList = (status: 'active' | 'completed' | 'all') => {
    const filtered = getFilteredSimulations(status);

    if (filtered.length === 0) {
      return (
        <div className="text-center py-8">
          {searchTerm ? (
            <div>
              <p className="text-muted-foreground mb-2">No simulations match your search</p>
              <Button variant="ghost" size="sm" onClick={handleClearSearch}>
                <FilterX className="h-4 w-4 mr-2" />
                Clear search
              </Button>
            </div>
          ) : (
            <p className="text-muted-foreground">
              {status === 'active'
                ? "No active simulations yet. Start a new simulation to see it here."
                : status === 'completed'
                  ? "No completed simulations found."
                  : "No simulations have been created yet."}
            </p>
          )}
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(simulation => (
          <SimulationCard
            key={simulation.id}
            simulation={simulation}
            onClick={() => setSelectedSimulation(simulation)}
          />
        ))}
      </div>
    );
  };

  return (
    <Layout>
      <div className="animate-fade-in">
        {selectedSimulation ? (
          <SimulationDetail
            simulation={selectedSimulation}
            onBack={() => setSelectedSimulation(null)}
          />
        ) : (
          <>
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">Simulations</h1>
                <p className="text-muted-foreground">
                  Run and analyze user simulations with AI personas
                </p>
              </div>
              <Button
                className="bg-uxagent-purple hover:bg-uxagent-dark-purple"
                onClick={() => setIsNewSimulationModalOpen(true)}
              >
                New Simulation
              </Button>
            </div>

            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search simulations..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            <Tabs defaultValue="active" className="w-full">
              <TabsList className="mb-4">
                <TabsTrigger value="active">Active</TabsTrigger>
                <TabsTrigger value="completed">Completed</TabsTrigger>
                <TabsTrigger value="all">All</TabsTrigger>
              </TabsList>

              <TabsContent value="active">
                <Card>
                  <CardHeader>
                    <CardTitle>Active Simulations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderSimulationList('active')}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="completed">
                <Card>
                  <CardHeader>
                    <CardTitle>Completed Simulations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderSimulationList('completed')}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="all">
                <Card>
                  <CardHeader>
                    <CardTitle>All Simulations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderSimulationList('all')}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            <NewSimulationModal
              open={isNewSimulationModalOpen}
              onOpenChange={setIsNewSimulationModalOpen}
              personas={personas}
              onSimulationCreated={handleCreateSimulation}
            />
          </>
        )}
      </div>
    </Layout>
  );
};

export default Simulations;
