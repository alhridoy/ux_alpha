
import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Loader2, Globe } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Persona, SimulationResult } from '@/types';
import { llmService } from '@/services/llmService';
import { backendService } from '@/services/backendService';

type NewSimulationModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  personas: Persona[];
  onSimulationCreated: (simulation: SimulationResult) => void;
};

type SimulationFormValues = {
  personaId: string;
  webUrl: string;
  task: string;
};

const NewSimulationModal = ({ open, onOpenChange, personas, onSimulationCreated }: NewSimulationModalProps) => {
  const [isRunning, setIsRunning] = useState(false);
  
  const form = useForm<SimulationFormValues>({
    defaultValues: {
      personaId: '',
      webUrl: '',
      task: '',
    }
  });

  const handleSubmit = async (data: SimulationFormValues) => {
    const selectedPersona = personas.find(p => p.id === data.personaId);
    if (!selectedPersona) {
      toast.error("Please select a persona first");
      return;
    }
    
    setIsRunning(true);
    try {
      // Check if we should use the backend or the mock implementation
      const backendConfigured = await backendService.getConfiguredProviders();
      
      if (backendConfigured.length > 0) {
        // Use the backend service to run the simulation
        const simulationId = await backendService.startSimulation(
          data.personaId,
          data.webUrl,
          data.task
        );
        
        if (!simulationId) {
          toast.error("Failed to start simulation");
          return;
        }
        
        // Poll for simulation status
        let completed = false;
        let result = null;
        
        while (!completed) {
          const status = await backendService.getSimulationStatus(simulationId);
          
          if (status.status === "completed") {
            completed = true;
            result = await backendService.getSimulationResult(simulationId);
          } else if (status.status === "failed") {
            toast.error(`Simulation failed: ${status.error}`);
            setIsRunning(false);
            return;
          }
          
          // Wait before polling again
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        if (result) {
          onSimulationCreated(result);
          toast.success("Simulation completed successfully!");
          onOpenChange(false);
        }
      } else {
        // Use the mock implementation from our service
        // In a real implementation, this would call your LLM Agent API
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Create a mock simulation result
        const mockSimulation: SimulationResult = {
          id: uuidv4(),
          persona: selectedPersona,
          webUrl: data.webUrl,
          task: data.task,
          taskCompleted: Math.random() > 0.3, // Random success/failure
          durationSeconds: Math.floor(Math.random() * 120) + 30, // 30-150 seconds
          actions: [
            {
              id: uuidv4(),
              timestamp: Date.now(),
              type: 'navigate',
              target: data.webUrl,
              reasoning: `Navigating to the provided URL to start the task: ${data.task}`
            },
            // In a real implementation, this would contain the full action trace
          ],
          reflections: [
            `As ${selectedPersona.name}, I approached this task with my ${selectedPersona.techExperience.toLowerCase()} level of tech experience.`,
            "The website layout was intuitive, though I did struggle with finding some elements.",
          ],
          wonderings: [
            "I wonder if other users would find this navigation structure confusing?",
            "Would a more prominent search bar improve the experience?",
          ],
          timestamp: Date.now(),
        };
        
        onSimulationCreated(mockSimulation);
        toast.success("Simulation completed successfully!");
        onOpenChange(false);
      }
    } catch (error) {
      console.error("Error running simulation:", error);
      toast.error("Failed to run simulation. Please try again.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Create New Simulation</DialogTitle>
          <DialogDescription>
            Configure a simulated user test with an AI persona
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="personaId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Select Persona</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a persona for this simulation" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {personas.length === 0 ? (
                        <SelectItem value="no-personas" disabled>
                          No personas available. Create one first.
                        </SelectItem>
                      ) : (
                        personas.map((persona) => (
                          <SelectItem key={persona.id} value={persona.id}>
                            {persona.name} - {persona.age}, {persona.occupation}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Choose which persona will perform this simulation
                  </FormDescription>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="webUrl"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Website URL</FormLabel>
                  <FormControl>
                    <Input placeholder="https://example.com" {...field} />
                  </FormControl>
                  <FormDescription>
                    Enter the URL of the website to test
                  </FormDescription>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="task"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Task Description</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Find and purchase a red sweater in size medium" 
                      className="min-h-[100px]"
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    Describe the task you want the persona to complete
                  </FormDescription>
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={isRunning || personas.length === 0} 
                className="bg-uxagent-purple hover:bg-uxagent-dark-purple"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Simulation...
                  </>
                ) : (
                  <>
                    <Globe className="mr-2 h-4 w-4" />
                    Run Simulation
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default NewSimulationModal;
