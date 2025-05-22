UXAgent: Simulating Usability Testing of Web Design with LLM Agents
Table of Contents
Introduction
System Architecture
Methodology
Key Innovations
Evaluation and Results
Limitations and Ethical Considerations
Applications and Impact
Conclusion
Introduction
Usability testing is a critical component of web design that helps identify issues in user interface and experience. However, traditional usability testing methods face significant challenges: they are time-consuming, expensive, difficult to scale, and often lack sufficient participant diversity. To address these issues, researchers from Northeastern University, Amazon, and the University of Notre Dame have developed UXAgent, a system that leverages large language model (LLM) agents to simulate usability testing of web designs.

UXAgent System OverviewFigure 1: Overview of the UXAgent system, showing the core components including the Persona Generator, LLM Agent, Universal Browser Connector, and interfaces for UX researchers.

UXAgent enables UX researchers to generate diverse virtual user personas, simulate their interactions with web interfaces, collect detailed action and reasoning traces, and conduct follow-up interviews with the virtual users. Rather than replacing human participants, UXAgent aims to augment traditional usability testing by providing early feedback on study designs and identifying potential issues before involving real users.

System Architecture
UXAgent comprises three main components working together to enable effective usability testing simulation:

Persona Generator: Creates diverse virtual personas based on user-defined demographic distributions using an example persona as a seed. These personas guide the behavior and preferences of LLM agents during the simulated usability tests.

LLM Agent Module: The core of the system, featuring a novel dual-loop architecture inspired by cognitive science's dual-process theory:

Fast Loop: Handles real-time interactions with the web environment
Slow Loop: Performs deliberate reasoning and planning
LLM Agent ArchitectureFigure 2: The dual-loop architecture of the LLM Agent, showing the Fast Loop (for perception, planning, and action) and Slow Loop (for reflection and wonder), with the Memory Stream connecting both loops.

Universal Browser Connector: Enables the LLM agent to interact with actual web environments through Chrome browser. It includes:
A simplified HTML parser that extracts relevant content from complex web pages
A task-agnostic action space allowing the agent to perform various web interactions
The Universal Browser Connector plays a crucial role in processing web content for the LLM agent:

Universal Browser ConnectorFigure 3: The Universal Browser Connector processes raw web pages into simplified HTML for the LLM agent's perception module, which then generates observation memory pieces.

Methodology
UXAgent incorporates several methodological innovations to ensure effective usability testing simulation:

HTML Parsing and Simplification
The system employs a simplified HTML parser that extracts semantically meaningful content from web pages while removing unnecessary visual-only elements:

HTML ParsingFigure 4: Illustration of HTML structure before and after parsing, showing how visual-only elements are removed to simplify the representation for the LLM agent.

Dual-Loop Processing
The LLM agent's architecture implements two distinct processing loops:

Fast Loop:

Perception Module: Observes and interprets the current web state
Planning Module: Determines the next action to take
Action Module: Executes the planned action on the web interface
Slow Loop:

Reflection Module: Periodically evaluates progress and adjusts strategies
Wonder Module: Generates spontaneous thoughts and questions that might occur to a human user
These loops are connected through a Memory Stream that maintains the agent's understanding of its interaction history and goals.

Agent Interview Interface
After completing a simulated usability test, UX researchers can conduct natural language interviews with the LLM agents to gather additional qualitative feedback:

Agent Interview InterfaceFigure 5: The Agent Interview Interface showing a conversation with a virtual customer, including their persona details and action trace.

Key Innovations
UXAgent introduces several innovations that distinguish it from existing approaches:

Dual-Loop Architecture: By separating fast, reactive processing from slower, deliberative reasoning, UXAgent balances the need for real-time responsiveness with the depth of reasoning required for realistic user simulation.

Simplified HTML Representation: Unlike systems that use screenshot-based approaches or complex DOM structures, UXAgent employs a simplified HTML representation that captures the essential semantic content while being processable by LLMs.

Comprehensive Data Collection: The system collects multiple data streams, including:

Action traces (what the user did)
Reasoning traces (why they did it)
Reflection and wonder traces (what they thought about during the process)
Interview responses (post-test feedback)
Persona-Based Simulation: Rather than using generic agents, UXAgent generates diverse personas with specific demographics, preferences, and needs that influence behavior during testing.

Evaluation and Results
The researchers conducted a heuristic evaluation with five UX researchers to assess UXAgent's effectiveness. Participants were asked to analyze simulation data generated by UXAgent for a shopping website.

Key findings from the evaluation included:

Positive Reception: UX researchers generally praised the innovation of the system and found the generated data helpful for iterating on study designs.

Trust Building Process: Participants initially focused on verifying the trustworthiness of the data before proceeding with deeper analysis.

Hypothesis Generation: The system aided in generating hypotheses that provided insights for future user studies with real participants.

Value of Qualitative Feedback: Participants particularly valued the ability to conduct natural language interviews with the LLM agents, finding this feature especially helpful for understanding user perspectives.

Mixed Feelings on Realism: While participants found the generated data helpful, they expressed some reservations about its realism, noting that the simulated human behavior could be "very detailed" and not entirely representative of real human interactions.

Research participants were able to observe simulated usability sessions through the Simulation Replay Interface:

Simulation Replay InterfaceFigure 6: The Simulation Replay Interface showing a recording of an LLM agent interacting with a web page during usability testing.

The system also demonstrated the ability to interact with complex web interfaces, such as flight booking sites:

LLM Agent Web InteractionFigure 7: An LLM agent interacting with Google Flights, showcasing the system's ability to handle complex web interfaces.

Limitations and Ethical Considerations
The researchers acknowledge several important limitations and ethical considerations:

Realism Concerns: LLM agents may not perfectly replicate human behavior, and their interactions may appear too systematic or detailed compared to real users.

Bias Issues: Potential biases in the underlying LLMs could be amplified in the generated personas and their behaviors, leading to skewed testing results.

Complexity Handling: While UXAgent can interact with many web interfaces, extremely complex or highly dynamic websites may pose challenges.

Privacy Considerations: Using LLM agents for usability testing raises privacy questions, particularly regarding the data used to train the models and the potential for extracting sensitive information.

Not a Replacement: The researchers emphasize that UXAgent is intended to complement, not replace, traditional usability testing with human participants.

Applications and Impact
UXAgent offers several potential applications and impacts for UX research and web design:

Improved Usability Testing Efficiency: By enabling rapid simulation of user interactions, UXAgent can help researchers identify potential issues early in the design process without the overhead of recruiting human participants.

Cost Reduction: The system can significantly reduce the cost associated with conducting usability studies, particularly for preliminary testing and iteration.

Increased Diversity: The ability to generate diverse personas allows testing with a broader range of simulated users than might be practically achievable with human participants.

Enhanced Study Design: UXAgent can help researchers refine their study protocols and task designs before conducting studies with real participants.

Democratization of UX Research: By reducing barriers to entry for usability testing, UXAgent could make UX research more accessible to smaller organizations and teams with limited resources.

Beyond usability testing, the researchers suggest that the underlying capabilities of LLM agents could be applied to:

Creating digital twins for end-user task automation
Evaluating existing AI systems
Simulating A/B testing with behavioral feedback