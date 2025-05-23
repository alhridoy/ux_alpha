
export type Persona = {
  id: string;
  name: string;
  age: number;
  gender: string;
  occupation: string;
  techExperience: 'Beginner' | 'Intermediate' | 'Advanced';
  traits: string[];
  goals: string[];
  painPoints: string[];
  profileImage: string;
};

export type ActionType = 
  | 'click'
  | 'input'
  | 'scroll'
  | 'hover'
  | 'navigate'
  | 'wait'
  | 'error';

export type AgentAction = {
  id: string;
  timestamp: number;
  type: ActionType;
  target?: string;
  value?: string;
  reasoning: string;
};

export type SimulationResult = {
  id: string;
  persona: Persona;
  webUrl: string;
  task: string;
  taskCompleted: boolean;
  durationSeconds: number;
  actions: AgentAction[];
  reflections: string[];
  wonderings: string[];
  timestamp: number;
};

export type Interview = {
  id: string;
  simulationId: string;
  questions: {
    question: string;
    answer: string;
  }[];
};

// Configuration types for the PersonaGenerator
export type PersonaGeneratorConfig = {
  count?: number;
  ageRange?: string;
  incomeDistribution?: string;
  educationLevels?: string[];
  shoppingInterests?: string[];
  techLiteracy?: string;
};

// Schema types for data extraction
export type ExtractionSchemaField = {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description?: string;
};

export type ExtractionSchema = {
  type: 'object';
  properties: Record<string, {
    type: string;
    description?: string;
  }>;
  required: string[];
};

export type ExtractionRequest = {
  url: string;
  instruction: string;
  schemaDefinition: ExtractionSchema;
};

export type ExtractionResult = {
  extractedData: any;
  executionTime: number;
};
