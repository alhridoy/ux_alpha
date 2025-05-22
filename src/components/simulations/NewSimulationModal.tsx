
import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Loader2, Globe, Download } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { useLocation } from 'react-router-dom';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Persona, SimulationResult } from '@/types';
import { llmService } from '@/services/llmService';
import { backendService } from '@/services/backendService';
import DataExtractionForm from './DataExtractionForm';

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
  const location = useLocation();
  const [isRunning, setIsRunning] = useState(false);
  const [automationType, setAutomationType] = useState<'selenium' | 'stagehand' | null>(null);
  const [isStagehandConfigured, setIsStagehandConfigured] = useState(false);
  const [activeTab, setActiveTab] = useState<'simulation' | 'extraction'>('simulation');
  const [webUrl, setWebUrl] = useState('');

  // Get the selected persona from location state if available
  const state = location.state as { selectedPersona?: Persona } | null;
  const selectedPersona = state?.selectedPersona;

  const form = useForm<SimulationFormValues>({
    defaultValues: {
      personaId: selectedPersona?.id || '',
      webUrl: '',
      task: '',
    }
  });

  useEffect(() => {
    if (open) {
      const checkAutomationType = async () => {
        const type = await backendService.getBrowserAutomationType();
        setAutomationType(type);

        if (type === 'stagehand') {
          const stagehandConfigured = await backendService.isStagehandConfigured();
          setIsStagehandConfigured(stagehandConfigured);

          if (!stagehandConfigured) {
            toast.warning("Stagehand is selected but not configured. The simulation may not run properly.");
          }
        }
      };

      checkAutomationType();
    }
  }, [open]);

  const handleSubmit = async (data: SimulationFormValues) => {
    // Update shared webUrl
    setWebUrl(data.webUrl);

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

        // Create a mock simulation result with automation type info
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
            {
              id: uuidv4(),
              timestamp: Date.now() + 2000,
              type: 'click',
              target: automationType === 'stagehand' ? 'AI identified element' : 'button_search',
              reasoning: automationType === 'stagehand'
                ? 'Using Stagehand AI to identify and click the search button'
                : 'Looking for the search button based on its element ID'
            },
            // In a real implementation, this would contain the full action trace
          ],
          reflections: [
            `As ${selectedPersona.name}, I approached this task with my ${selectedPersona.techExperience.toLowerCase()} level of tech experience.`,
            automationType === 'stagehand'
              ? "The Stagehand AI helped me navigate the site more naturally, focusing on what elements do rather than their technical details."
              : "The website layout was intuitive, though I did struggle with finding some elements.",
          ],
          wonderings: [
            "I wonder if other users would find this navigation structure confusing?",
            automationType === 'stagehand'
              ? "Would the AI automation handle a more complex workflow as effectively?"
              : "Would a more prominent search bar improve the experience?",
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

  const handleWebUrlChange = (url: string) => {
    form.setValue('webUrl', url);
    setWebUrl(url);
  };

  const handleExtractedData = (data: any) => {
    toast.success("Data extracted successfully!");
    // You can add additional logic here to use the extracted data
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>Browser Automation</DialogTitle>
          <DialogDescription>
            Configure browser automation with AI personas or extract data
            {automationType === 'stagehand' && (
              <span className="block mt-1 text-xs bg-green-50 text-green-700 p-1 rounded">
                Using Stagehand AI-powered browser automation
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'simulation' | 'extraction')}>
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="simulation">Run Simulation</TabsTrigger>
            <TabsTrigger value="extraction">Extract Data</TabsTrigger>
          </TabsList>

          <TabsContent value="simulation">
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
                        <Input
                          placeholder="https://example.com"
                          {...field}
                          onChange={(e) => {
                            field.onChange(e);
                            handleWebUrlChange(e.target.value);
                          }}
                        />
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
                        {automationType === 'stagehand' && (
                          <span className="block mt-1 text-xs text-green-600">
                            Stagehand AI will understand natural language task descriptions
                          </span>
                        )}
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
          </TabsContent>

          <TabsContent value="extraction">
            <div className="space-y-4">
              <FormItem>
                <FormLabel>Website URL</FormLabel>
                <Input
                  placeholder="https://example.com"
                  value={webUrl}
                  onChange={(e) => setWebUrl(e.target.value)}
                />
                <FormDescription>
                  Enter the URL of the website to extract data from
                </FormDescription>
              </FormItem>

              <DataExtractionForm
                webUrl={webUrl}
                onDataExtracted={handleExtractedData}
              />
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default NewSimulationModal;
