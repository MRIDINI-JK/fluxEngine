Phase 6 Architeture 
                         FluxEngine
                             │
             ┌───────────────┴───────────────┐
             │                               │
        Workflow Core                  Event Bus
             │                               │
      ┌──────┴──────┐                  RabbitMQ
      │             │
   Parser         Graph
      │             │
      └──────┬──────┘
             │
         Validator
             │
         Compiler
             │
             ▼
      ┌──────────────┐
      │   Executor   │
      └──────┬───────┘
             │
      ┌──────┼─────────┐
      │      │         │
    State  Retry   Checkpoint
      │      │         │
      └──────┼─────────┘
             │
             ▼
        Task Execution