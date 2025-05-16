
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
  | 'wait';

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
