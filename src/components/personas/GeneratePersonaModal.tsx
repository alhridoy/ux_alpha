
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { v4 as uuidv4 } from 'uuid';
import { Loader2, UserPlus } from 'lucide-react';
import { toast } from 'sonner';

import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { PersonaGeneratorConfig, Persona } from '@/types';

// Placeholder for actual API call - this would be replaced with real API integration
const generatePersonas = async (config: PersonaGeneratorConfig): Promise<Persona[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const getRandomProfileImage = () => {
    const images = [
      'https://images.unsplash.com/photo-1607746882042-944635dfe10e',
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330',
      'https://images.unsplash.com/photo-1599566150163-29194dcaad36',
      'https://images.unsplash.com/photo-1552058544-f2b08422138a'
    ];
    return images[Math.floor(Math.random() * images.length)];
  };

  // Generate a mock persona
  // In a real implementation, this would call an API that interfaces with the LLM
  const techExperiences = ['Beginner', 'Intermediate', 'Advanced'] as const;
  const genders = ['Male', 'Female', 'Non-binary'];
  const occupations = ['Software Developer', 'Marketing Manager', 'Teacher', 'Doctor', 'Student', 'Retired'];

  return Array(config.count || 1).fill(0).map(() => {
    const techExperience = techExperiences[Math.floor(Math.random() * techExperiences.length)];
    
    return {
      id: uuidv4(),
      name: `Generated Persona ${Math.floor(Math.random() * 1000)}`,
      age: Math.floor(Math.random() * (65 - 18) + 18),
      gender: genders[Math.floor(Math.random() * genders.length)],
      occupation: occupations[Math.floor(Math.random() * occupations.length)],
      techExperience: techExperience,
      traits: ['adaptable', 'curious', 'detail-oriented'],
      goals: ['Find information quickly', 'Complete tasks efficiently', 'Learn new technologies'],
      painPoints: ['Complex interfaces', 'Slow loading times', 'Too many options'],
      profileImage: getRandomProfileImage()
    };
  });
};

type GeneratePersonaModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onPersonasGenerated: (personas: Persona[]) => void;
};

const GeneratePersonaModal = ({ open, onOpenChange, onPersonasGenerated }: GeneratePersonaModalProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  
  const form = useForm<PersonaGeneratorConfig>({
    defaultValues: {
      count: 1,
      ageRange: "18-65",
      incomeDistribution: "diverse",
      educationLevels: ["bachelor", "masters"],
      shoppingInterests: ["electronics", "fashion", "home goods"],
      techLiteracy: "moderate"
    }
  });

  const handleSubmit = async (data: PersonaGeneratorConfig) => {
    setIsGenerating(true);
    try {
      const personas = await generatePersonas(data);
      onPersonasGenerated(personas);
      toast.success(`Successfully generated ${personas.length} persona${personas.length > 1 ? 's' : ''}`);
      onOpenChange(false);
    } catch (error) {
      console.error("Error generating personas:", error);
      toast.error("Failed to generate personas. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Generate New Personas</DialogTitle>
          <DialogDescription>
            Create AI-generated personas based on your specifications.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="count"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Number of Personas</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={1}
                      max={10}
                      {...field}
                      onChange={e => field.onChange(parseInt(e.target.value))}
                    />
                  </FormControl>
                  <FormDescription>
                    Choose how many personas to generate (1-10)
                  </FormDescription>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="ageRange"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Age Range</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. 25-45" {...field} />
                  </FormControl>
                  <FormDescription>
                    Specify the age range for the generated personas
                  </FormDescription>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="techLiteracy"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tech Literacy</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select tech literacy level" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="moderate">Moderate</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="diverse">Diverse</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Choose the technical literacy level for your personas
                  </FormDescription>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="incomeDistribution"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Income Distribution</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. middle to upper-middle class" {...field} />
                  </FormControl>
                  <FormDescription>
                    Describe the income distribution for the personas
                  </FormDescription>
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={isGenerating} className="bg-uxagent-purple hover:bg-uxagent-dark-purple">
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Generate Personas
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

export default GeneratePersonaModal;
