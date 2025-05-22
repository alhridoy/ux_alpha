import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Persona } from '@/types';
import { samplePersonas } from '@/data/sampleData';

interface PersonasContextType {
  personas: Persona[];
  setPersonas: React.Dispatch<React.SetStateAction<Persona[]>>;
  addPersona: (persona: Persona) => void;
  addPersonas: (newPersonas: Persona[]) => void;
}

const PersonasContext = createContext<PersonasContextType | undefined>(undefined);

export const PersonasProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [personas, setPersonas] = useState<Persona[]>(samplePersonas);

  const addPersona = (persona: Persona) => {
    setPersonas(prev => [...prev, persona]);
  };

  const addPersonas = (newPersonas: Persona[]) => {
    setPersonas(prev => [...prev, ...newPersonas]);
  };

  return (
    <PersonasContext.Provider value={{ personas, setPersonas, addPersona, addPersonas }}>
      {children}
    </PersonasContext.Provider>
  );
};

export const usePersonas = (): PersonasContextType => {
  const context = useContext(PersonasContext);
  if (context === undefined) {
    throw new Error('usePersonas must be used within a PersonasProvider');
  }
  return context;
};
