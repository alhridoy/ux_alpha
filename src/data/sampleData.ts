
import { Persona, SimulationResult, Interview } from '@/types';

export const samplePersonas: Persona[] = [
  {
    id: '1',
    name: 'Emily Chen',
    age: 28,
    gender: 'Female',
    occupation: 'Marketing Manager',
    techExperience: 'Intermediate',
    traits: ['detail-oriented', 'impatient', 'visual thinker'],
    goals: ['Find products quickly', 'Compare options easily'],
    painPoints: ['Complicated checkout processes', 'Unclear pricing'],
    profileImage: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330',
  },
  {
    id: '2',
    name: 'James Wilson',
    age: 42,
    gender: 'Male',
    occupation: 'Financial Analyst',
    techExperience: 'Beginner',
    traits: ['methodical', 'cautious', 'thorough'],
    goals: ['Ensure transactions are secure', 'Find detailed information'],
    painPoints: ['Small text', 'Too many form fields'],
    profileImage: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36',
  },
  {
    id: '3',
    name: 'Maya Johnson',
    age: 19,
    gender: 'Female',
    occupation: 'College Student',
    techExperience: 'Advanced',
    traits: ['quick learner', 'impatient', 'multitasker'],
    goals: ['Find best deals', 'Quick checkout'],
    painPoints: ['Slow loading pages', 'Required account creation'],
    profileImage: 'https://images.unsplash.com/photo-1607746882042-944635dfe10e',
  },
  {
    id: '4',
    name: 'Robert Garcia',
    age: 65,
    gender: 'Male',
    occupation: 'Retired Teacher',
    techExperience: 'Beginner',
    traits: ['patient', 'traditional', 'detail-oriented'],
    goals: ['Accomplish tasks with minimal steps', 'Understand all options'],
    painPoints: ['Too many animations', 'Complicated navigation'],
    profileImage: 'https://images.unsplash.com/photo-1552058544-f2b08422138a',
  },
];

export const sampleSimulations: SimulationResult[] = [
  {
    id: '1',
    persona: samplePersonas[0],
    webUrl: 'https://ecommerce-sample.com',
    task: 'Purchase a pair of running shoes that match your preferences.',
    taskCompleted: true,
    durationSeconds: 187,
    actions: [
      {
        id: '1',
        timestamp: 1715412000000,
        type: 'navigate',
        target: 'homepage',
        reasoning: 'Exploring the website to find the athletic section',
      },
      {
        id: '2',
        timestamp: 1715412010000,
        type: 'click',
        target: 'navigation: Athletic',
        reasoning: 'Looking for running shoes in the athletic category',
      },
      {
        id: '3',
        timestamp: 1715412020000,
        type: 'click',
        target: 'filter: Running',
        reasoning: 'Narrowing down to running shoes specifically',
      },
      {
        id: '4',
        timestamp: 1715412040000,
        type: 'click',
        target: 'sort: Price low to high',
        reasoning: 'Want to compare options starting with less expensive ones',
      },
      {
        id: '5',
        timestamp: 1715412060000,
        type: 'click',
        target: 'product: Nike Air Zoom',
        reasoning: 'These shoes look appealing and have good reviews',
      },
      {
        id: '6',
        timestamp: 1715412090000,
        type: 'click',
        target: 'size: 8',
        reasoning: 'Selecting my standard size',
      },
      {
        id: '7',
        timestamp: 1715412100000,
        type: 'click',
        target: 'color: Black/White',
        reasoning: 'Prefer neutral colors that match with everything',
      },
      {
        id: '8',
        timestamp: 1715412110000,
        type: 'click',
        target: 'button: Add to cart',
        reasoning: 'Ready to purchase these shoes',
      },
      {
        id: '9',
        timestamp: 1715412130000,
        type: 'click',
        target: 'button: Checkout',
        reasoning: 'Proceeding to payment',
      },
      {
        id: '10',
        timestamp: 1715412180000,
        type: 'click',
        target: 'button: Complete Order',
        reasoning: 'Finishing the purchase process',
      },
    ],
    reflections: [
      'The filter options were helpful in narrowing down my search.',
      'I was confused by the size guide - it wasn\'t immediately clear which sizing system was being used.',
      'The checkout process was streamlined and efficient.',
    ],
    wonderings: [
      'Do they offer free returns if the shoes don\'t fit?',
      'I wonder if there are any loyalty programs or discounts for first-time buyers?',
      'Would be nice to see more color options for these shoes.',
    ],
    timestamp: 1715412000000,
  },
  {
    id: '2',
    persona: samplePersonas[1],
    webUrl: 'https://banking-sample.com',
    task: 'Transfer $500 from your checking account to your savings account.',
    taskCompleted: false,
    durationSeconds: 243,
    actions: [
      {
        id: '1',
        timestamp: 1715498400000,
        type: 'click',
        target: 'button: Login',
        reasoning: 'Need to access my account',
      },
      {
        id: '2',
        timestamp: 1715498420000,
        type: 'input',
        target: 'field: Username',
        value: 'jwilson',
        reasoning: 'Entering my username',
      },
      {
        id: '3',
        timestamp: 1715498430000,
        type: 'input',
        target: 'field: Password',
        value: '********',
        reasoning: 'Entering my password',
      },
      {
        id: '4',
        timestamp: 1715498440000,
        type: 'click',
        target: 'button: Sign In',
        reasoning: 'Submitting login credentials',
      },
      {
        id: '5',
        timestamp: 1715498460000,
        type: 'click',
        target: 'navigation: Transfers',
        reasoning: 'Looking for the transfer function',
      },
      {
        id: '6',
        timestamp: 1715498480000,
        type: 'click',
        target: 'dropdown: From Account',
        reasoning: 'Need to select my checking account',
      },
      {
        id: '7',
        timestamp: 1715498490000,
        type: 'click',
        target: 'option: Checking Account (...1234)',
        reasoning: 'This is my checking account',
      },
      {
        id: '8',
        timestamp: 1715498500000,
        type: 'click',
        target: 'dropdown: To Account',
        reasoning: 'Need to select my savings account',
      },
      {
        id: '9',
        timestamp: 1715498510000,
        type: 'click',
        target: 'option: Savings Account (...5678)',
        reasoning: 'This is my savings account',
      },
      {
        id: '10',
        timestamp: 1715498520000,
        type: 'input',
        target: 'field: Amount',
        value: '500',
        reasoning: 'Entering the transfer amount',
      },
      {
        id: '11',
        timestamp: 1715498540000,
        type: 'click',
        target: 'button: Review Transfer',
        reasoning: 'Want to verify the details before confirming',
      },
      {
        id: '12',
        timestamp: 1715498560000,
        type: 'error',
        target: 'error message: Session timeout',
        reasoning: 'Unexpected timeout error, couldn\'t complete the task',
      },
    ],
    reflections: [
      'The navigation was clear until I reached the transfer page.',
      'It wasn\'t immediately obvious that I needed to click "Review Transfer" before confirming.',
      'The timeout occurred without warning and I lost all my entered information.',
    ],
    wonderings: [
      'Why does the session timeout so quickly without any countdown or warning?',
      'Could there be a way to save the transfer information as a draft?',
      'Is there a mobile app that might be more stable for transactions?',
    ],
    timestamp: 1715498400000,
  },
];

export const sampleInterviews: Interview[] = [
  {
    id: '1',
    simulationId: '1',
    questions: [
      {
        question: 'What was your overall impression of the shopping experience?',
        answer: 'Overall, I found the shopping experience to be smooth and intuitive. The website had a clean design that made it easy to navigate through different categories. The filter options were particularly helpful in narrowing down my search for running shoes.'
      },
      {
        question: 'Did you encounter any difficulties during the checkout process?',
        answer: 'The checkout process was mostly straightforward, but I did notice that the shipping options weren\'t very clear. It wasn\'t immediately obvious which shipping method would be fastest, and I had to read through several options to figure it out. Also, I would have appreciated a more prominent display of the estimated delivery date.'
      },
      {
        question: 'What improvements would you suggest for the website?',
        answer: 'I think the product pages could include more detailed information about materials and care instructions. Also, the size guide was a bit confusing - it would be helpful to have a more interactive sizing tool. Lastly, I\'d love to see a feature that lets me save items to different wishlists or categories for future reference.'
      }
    ]
  },
  {
    id: '2',
    simulationId: '2',
    questions: [
      {
        question: 'Why do you think your banking transfer was unsuccessful?',
        answer: 'The session timeout was the primary issue. I was taking my time to carefully verify all the details before submitting the transfer, which is important for financial transactions. The system seems to have a very short timeout period that doesn\'t account for users who might need more time to review their actions, especially for sensitive financial operations.'
      },
      {
        question: 'How did the timeout make you feel?',
        answer: 'Frustrated and concerned. Frustrated because I had to start the process over again, and concerned because it made me question the reliability of the platform. For banking websites, users need to feel confident that the system is stable and won\'t interrupt important transactions. The abrupt timeout without warning damaged my trust in the platform.'
      },
      {
        question: 'What security features did you notice during your experience?',
        answer: 'I noticed the standard username and password authentication, but was surprised there wasn\'t two-factor authentication for a banking website. I also appreciated that the system masked my password during entry. However, the quick timeout might be a security feature, though it needs to be implemented more thoughtfully with warnings and the ability to extend the session if the user is actively reviewing information.'
      }
    ]
  }
];
