
import { v4 as uuidv4 } from 'uuid';
import { ActionType, AgentAction, Persona, SimulationResult } from '@/types';

// This would be replaced with an actual API call to OpenAI or another LLM provider
const generateAgentActions = async (
  persona: Persona,
  webUrl: string,
  task: string
): Promise<AgentAction[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock the different action types
  const actionTypes: ActionType[] = ['click', 'input', 'scroll', 'hover', 'navigate', 'wait'];
  
  // Generate a sequence of mock actions
  const mockActions: AgentAction[] = [];
  const actionCount = Math.floor(Math.random() * 15) + 5; // 5-20 actions
  
  let currentTime = Date.now();
  
  // First action is always navigation
  mockActions.push({
    id: uuidv4(),
    timestamp: currentTime,
    type: 'navigate',
    target: webUrl,
    reasoning: `Navigating to the website to begin the task: ${task}`
  });
  
  // Generate subsequent actions
  for (let i = 1; i < actionCount; i++) {
    currentTime += Math.floor(Math.random() * 10000) + 1000; // 1-11 seconds between actions
    
    const actionType = actionTypes[Math.floor(Math.random() * actionTypes.length)];
    
    let action: AgentAction = {
      id: uuidv4(),
      timestamp: currentTime,
      type: actionType,
      reasoning: generateReasoningBasedOnPersona(persona, actionType, task)
    };
    
    // Add action-specific properties
    switch (actionType) {
      case 'click':
        action.target = generateMockSelector();
        break;
      case 'input':
        action.target = generateMockSelector('input');
        action.value = generateMockInput(persona, task);
        break;
      case 'scroll':
        action.value = Math.random() > 0.5 ? 'down' : 'up';
        break;
      case 'hover':
        action.target = generateMockSelector();
        break;
      case 'navigate':
        action.target = generateMockUrl(webUrl);
        break;
      case 'error':
        action.reasoning = `Encountered an error: ${generateMockError()}`;
        break;
    }
    
    mockActions.push(action);
  }
  
  return mockActions;
};

const generateReasoningBasedOnPersona = (persona: Persona, actionType: ActionType, task: string): string => {
  const reasonings = [
    `As a ${persona.techExperience.toLowerCase()} tech user, I'm ${actionType === 'wait' ? 'taking time to find' : 'looking for'} the right option to complete my task.`,
    `I want to ${task.toLowerCase()}, so I'm ${actionType}ing on what seems most relevant.`,
    `Based on my experience as a ${persona.occupation.toLowerCase()}, I'm trying to efficiently ${actionType} to find what I need.`,
    `Given my goal to ${task.toLowerCase()}, this ${actionType} action seems most logical.`,
    `With my ${persona.traits.join(' and ')} personality, I tend to ${actionType} on elements that catch my attention.`
  ];
  
  return reasonings[Math.floor(Math.random() * reasonings.length)];
};

const generateMockSelector = (type: string = 'button'): string => {
  const selectors = [
    `#search-${type}`,
    `.navigation__${type}`,
    `[data-testid="main-${type}"]`,
    `.product-${type}--primary`,
    `#${type}-submit`
  ];
  
  return selectors[Math.floor(Math.random() * selectors.length)];
};

const generateMockInput = (persona: Persona, task: string): string => {
  if (task.toLowerCase().includes('search')) return 'product keywords';
  if (task.toLowerCase().includes('login')) return 'username';
  if (task.toLowerCase().includes('purchase')) return 'billing information';
  return 'user input text';
};

const generateMockUrl = (baseUrl: string): string => {
  const paths = ['/products', '/category/clothing', '/search-results', '/cart', '/checkout'];
  return `${baseUrl}${paths[Math.floor(Math.random() * paths.length)]}`;
};

const generateMockError = (): string => {
  const errors = [
    'Element not found in DOM',
    'Page timeout',
    'Network request failed',
    'Invalid form submission',
    'Button is not clickable'
  ];
  
  return errors[Math.floor(Math.random() * errors.length)];
};

export const runSimulation = async (
  persona: Persona,
  webUrl: string,
  task: string
): Promise<SimulationResult> => {
  try {
    const actions = await generateAgentActions(persona, webUrl, task);
    
    // In a real implementation, this would run a full simulation with the browser connector
    // and collect detailed results. For now, we'll generate mock data.
    
    const lastAction = actions[actions.length - 1];
    const isSuccessful = lastAction.type !== 'error' && Math.random() > 0.2;
    
    // Calculate total duration from first to last action
    const durationSeconds = Math.round((actions[actions.length - 1].timestamp - actions[0].timestamp) / 1000);
    
    // Generate reflections based on the persona and task
    const reflections = [
      `As ${persona.name} with ${persona.techExperience.toLowerCase()} tech experience, I ${isSuccessful ? 'was able to complete' : 'struggled with'} this task.`,
      `The website's layout was ${Math.random() > 0.5 ? 'intuitive' : 'confusing'} for someone with my background in ${persona.occupation}.`,
      `My ${persona.traits.join(' and ')} traits influenced how I approached the navigation.`
    ];
    
    // Generate wonderings (thoughts about the experience)
    const wonderings = [
      `I wonder if other users would find the ${Math.random() > 0.5 ? 'search functionality' : 'navigation'} as ${Math.random() > 0.5 ? 'helpful' : 'confusing'} as I did?`,
      `Would someone with ${persona.techExperience === 'Beginner' ? 'more' : 'less'} technical experience have an easier time?`,
      `How much does my background as a ${persona.occupation} affect my perception of this interface?`
    ];
    
    // Create the simulation result
    const result: SimulationResult = {
      id: uuidv4(),
      persona,
      webUrl,
      task,
      taskCompleted: isSuccessful,
      durationSeconds,
      actions,
      reflections,
      wonderings,
      timestamp: Date.now()
    };
    
    return result;
  } catch (error) {
    console.error("Error running simulation:", error);
    throw new Error("Failed to run simulation");
  }
};

// In a real implementation, this would call an LLM API to generate personas
export const generatePersonas = async (count: number = 1): Promise<Persona[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const mockPersonas: Persona[] = [];
  
  const firstNames = ['Alex', 'Jordan', 'Morgan', 'Taylor', 'Casey', 'Riley', 'Quinn', 'Jamie'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Miller', 'Davis', 'Garcia'];
  const occupations = ['Teacher', 'Software Developer', 'Marketing Manager', 'Retail Worker', 'Student', 'Retired', 'Healthcare Worker', 'Business Owner'];
  const genders = ['Male', 'Female', 'Non-binary'];
  const techLevels = ['Beginner', 'Intermediate', 'Advanced'] as const;
  const traits = ['adaptable', 'analytical', 'cautious', 'creative', 'detail-oriented', 'efficient', 'independent', 'organized', 'patient', 'practical', 'proactive', 'reliable', 'resourceful', 'thorough'];
  const goals = [
    'Find information quickly',
    'Complete tasks efficiently',
    'Avoid making mistakes',
    'Learn new technologies',
    'Stay updated with trends',
    'Maximize productivity',
    'Make informed decisions',
    'Simplify complex processes'
  ];
  const painPoints = [
    'Complex interfaces',
    'Slow loading times',
    'Too many options',
    'Confusing navigation',
    'Lack of visual cues',
    'Technical jargon',
    'Small text or buttons',
    'Inconsistent design patterns'
  ];
  const profileImages = [
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330',
    'https://images.unsplash.com/photo-1599566150163-29194dcaad36',
    'https://images.unsplash.com/photo-1552058544-f2b08422138a',
    'https://images.unsplash.com/photo-1569913486515-b74bf7751574',
    'https://images.unsplash.com/photo-1580489944761-15a19d654956',
  ];
  
  for (let i = 0; i < count; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const age = Math.floor(Math.random() * 50) + 18; // 18-68
    
    // Select 2-3 random traits
    const personaTraits = [];
    const traitCount = Math.floor(Math.random() * 2) + 2; // 2-3 traits
    for (let j = 0; j < traitCount; j++) {
      const trait = traits[Math.floor(Math.random() * traits.length)];
      if (!personaTraits.includes(trait)) {
        personaTraits.push(trait);
      }
    }
    
    // Select 2-3 random goals
    const personaGoals = [];
    const goalCount = Math.floor(Math.random() * 2) + 2; // 2-3 goals
    for (let j = 0; j < goalCount; j++) {
      const goal = goals[Math.floor(Math.random() * goals.length)];
      if (!personaGoals.includes(goal)) {
        personaGoals.push(goal);
      }
    }
    
    // Select 2-3 random pain points
    const personaPainPoints = [];
    const painPointCount = Math.floor(Math.random() * 2) + 2; // 2-3 pain points
    for (let j = 0; j < painPointCount; j++) {
      const painPoint = painPoints[Math.floor(Math.random() * painPoints.length)];
      if (!personaPainPoints.includes(painPoint)) {
        personaPainPoints.push(painPoint);
      }
    }
    
    mockPersonas.push({
      id: uuidv4(),
      name: `${firstName} ${lastName}`,
      age,
      gender: genders[Math.floor(Math.random() * genders.length)],
      occupation: occupations[Math.floor(Math.random() * occupations.length)],
      techExperience: techLevels[Math.floor(Math.random() * techLevels.length)],
      traits: personaTraits,
      goals: personaGoals,
      painPoints: personaPainPoints,
      profileImage: profileImages[Math.floor(Math.random() * profileImages.length)]
    });
  }
  
  return mockPersonas;
};
