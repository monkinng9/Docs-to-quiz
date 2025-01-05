## Goal
- Use CrewAI Agents to summarize a document and guide study
- Use CrewAI Agents to plan quiz
  - breakdown of topics
  - number of questions
  - question types
  - question difficulty
  - output to json file to let user modify
- Use CrewAI Agents to create a quiz according to the plan
- Use CrewAI Agents answer questions and output to json
- User do quiz
- Use CrewAI Agents to check answer and give feedback
- Use OpenLIT to observe agents

## Diagram
```mermaid
flowchart TB
    %% Main nodes
    Start([Start]) --> Doc[Input Document]
    
    %% Study Phase
    Doc --> StudyAgents[Study Agents]
    StudyAgents --> Summary[Document Summary]
    StudyAgents --> Guide[Study Guide]
    
    %% Quiz Planning Phase
    Summary & Guide --> QuizPlanner[Quiz Planning Agents]
    QuizPlanner --> Plan{Quiz Plan<br/>JSON}
    Plan --> |Manual Review|Modified{Modified Plan<br/>JSON}
    
    %% Quiz Creation Phase
    Modified --> QuizCreator[Quiz Creation Agents]
    QuizCreator --> Quiz{Quiz<br/>JSON}
    
    %% Quiz Taking Phase
    Quiz --> Interface[Quiz Interface]
    Interface --> |Student Takes Quiz|Answers{Student<br/>Answers}
    Answers --> CheckAgents[Answer Checking Agents]
    CheckAgents --> Feedback[Feedback & Score]
    
    %% OpenLIT Monitoring
    Monitor[[OpenLIT Monitor]]
    Monitor -.-|Observes|StudyAgents & QuizPlanner & QuizCreator & CheckAgents
    
    %% Styling
    classDef agents fill:#f9f,stroke:#333,stroke-width:2px
    classDef data fill:#fff,stroke:#333,stroke-width:2px
    classDef json fill:#fcf,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    classDef monitor fill:#ccf,stroke:#333,stroke-width:2px
    classDef start fill:#9f9,stroke:#333,stroke-width:2px
    
    class StudyAgents,QuizPlanner,QuizCreator,CheckAgents agents
    class Summary,Guide,Interface,Feedback data
    class Plan,Modified,Quiz,Answers json
    class Monitor monitor
    class Start start
    class Doc data
```

## Design

### Section 1: Study Phase
- Goals:
  - Use CrewAI Agents to summarize a document and guide study
- Use Deepseek V3 via LiteLLM - Openrouter
- 'Summarize and study guide' crew