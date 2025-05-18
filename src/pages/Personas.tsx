
import React, { useState } from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Search, Filter, UserPlus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { samplePersonas } from '@/data/sampleData';
import { Persona } from '@/types';
import GeneratePersonaModal from '@/components/personas/GeneratePersonaModal';

const Personas = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [personas, setPersonas] = useState<Persona[]>(samplePersonas);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  
  const filteredPersonas = personas.filter((persona) => 
    persona.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    persona.occupation.toLowerCase().includes(searchTerm.toLowerCase()) ||
    persona.techExperience.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handlePersonasGenerated = (newPersonas: Persona[]) => {
    setPersonas([...personas, ...newPersonas]);
    if (newPersonas.length > 0) {
      setSelectedPersona(newPersonas[0]);
    }
  };
  
  return (
    <Layout>
      <div className="animate-fade-in">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">Personas</h1>
            <p className="text-muted-foreground">
              Create and manage virtual users with diverse characteristics
            </p>
          </div>
          <Button 
            className="bg-uxagent-purple hover:bg-uxagent-dark-purple"
            onClick={() => setIsGenerateModalOpen(true)}
          >
            <UserPlus className="h-4 w-4 mr-2" />
            New Persona
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Persona Library</CardTitle>
                <CardDescription>Select a persona to view details</CardDescription>
                <div className="relative mt-2">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input 
                    placeholder="Search personas..." 
                    className="pl-8"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)} 
                  />
                </div>
              </CardHeader>
              <CardContent className="max-h-[500px] overflow-y-auto">
                <div className="space-y-2">
                  {filteredPersonas.length === 0 ? (
                    <p className="text-center p-4 text-muted-foreground text-sm">
                      No personas match your search
                    </p>
                  ) : (
                    filteredPersonas.map((persona) => (
                      <div 
                        key={persona.id}
                        className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${selectedPersona?.id === persona.id ? 'bg-uxagent-light-purple' : 'hover:bg-muted'}`}
                        onClick={() => setSelectedPersona(persona)}
                      >
                        <div className="h-10 w-10 rounded-full overflow-hidden flex-shrink-0 mr-3">
                          <img 
                            src={`${persona.profileImage}?w=80&h=80&fit=crop&crop=faces&auto=format`} 
                            alt={persona.name}
                            className="h-full w-full object-cover" 
                          />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{persona.name}</p>
                          <p className="text-xs text-muted-foreground">{persona.occupation}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between border-t p-4">
                <Button variant="outline" size="sm">
                  <Filter className="h-3.5 w-3.5 mr-1.5" />
                  Filter
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setIsGenerateModalOpen(true)}
                >
                  <Plus className="h-3.5 w-3.5 mr-1.5" />
                  Generate
                </Button>
              </CardFooter>
            </Card>
          </div>
          
          <div className="lg:col-span-2">
            {selectedPersona ? (
              <Card className="animate-fade-in">
                <CardHeader className="pb-3">
                  <div className="flex items-center">
                    <div className="h-16 w-16 rounded-full overflow-hidden mr-4">
                      <img 
                        src={`${selectedPersona.profileImage}?w=160&h=160&fit=crop&crop=faces&auto=format`}
                        alt={selectedPersona.name}
                        className="h-full w-full object-cover" 
                      />
                    </div>
                    <div>
                      <CardTitle className="text-2xl">{selectedPersona.name}</CardTitle>
                      <CardDescription className="flex items-center mt-1">
                        {selectedPersona.age} years old, {selectedPersona.gender} • {selectedPersona.occupation}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex mt-3">
                    <Badge variant="outline" className="mr-2">
                      {selectedPersona.techExperience} tech user
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  <div>
                    <h3 className="font-semibold mb-2 text-sm text-muted-foreground">TRAITS</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedPersona.traits.map((trait, index) => (
                        <Badge key={index} className="bg-uxagent-light-purple text-uxagent-dark-purple hover:bg-uxagent-light-purple">
                          {trait}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2 text-sm text-muted-foreground">GOALS</h3>
                    <ul className="list-disc pl-5 space-y-1">
                      {selectedPersona.goals.map((goal, index) => (
                        <li key={index} className="text-sm">{goal}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2 text-sm text-muted-foreground">PAIN POINTS</h3>
                    <ul className="list-disc pl-5 space-y-1">
                      {selectedPersona.painPoints.map((painPoint, index) => (
                        <li key={index} className="text-sm">{painPoint}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
                
                <CardFooter className="border-t pt-4 flex flex-col sm:flex-row gap-2">
                  <Button className="bg-uxagent-purple hover:bg-uxagent-dark-purple sm:flex-1">
                    Run Simulation with This Persona
                  </Button>
                  <Button variant="outline" className="sm:flex-1">
                    Edit Persona
                  </Button>
                </CardFooter>
              </Card>
            ) : (
              <div className="h-full flex flex-col items-center justify-center p-8 bg-white rounded-lg border border-dashed">
                <div className="w-16 h-16 bg-uxagent-light-purple rounded-full flex items-center justify-center mb-4">
                  <UserPlus className="h-8 w-8 text-uxagent-purple" />
                </div>
                <h3 className="text-lg font-medium mb-1">Select a Persona</h3>
                <p className="text-muted-foreground text-center max-w-md mb-4">
                  Choose a persona from the library to view details or create a new one
                </p>
                <Button onClick={() => setIsGenerateModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Persona
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      <GeneratePersonaModal 
        open={isGenerateModalOpen} 
        onOpenChange={setIsGenerateModalOpen} 
        onPersonasGenerated={handlePersonasGenerated} 
      />
    </Layout>
  );
};

export default Personas;
