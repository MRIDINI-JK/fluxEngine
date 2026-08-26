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


Phase 7 Architecture

                       ┌───────────────────┐
                       │  Workflow Engine  │
                       └─────────┬─────────┘
                                 │
                          task.dispatched
                                 │
                                 ▼
                         ┌──────────────┐
                         │   RabbitMQ   │
                         └───────┬──────┘
                                 │
                     ┌───────────┼───────────┐
                     │           │           │
                     ▼           ▼           ▼
                 Worker 1    Worker 2    Worker 3
                 Python      HTTP        LLM
                     │           │           │
                     └───────────┼───────────┘
                                 │
                            task.result
                                 │
                                 ▼
                         ┌──────────────┐
                         │   RabbitMQ   │
                         └───────┬──────┘
                                 │
                                 ▼
                       Workflow Executor


                         FLUXENGINE
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   REST API             Scheduler          WebSocket
        │                    │                    │
        │             Cron / Timer              │
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                         RabbitMQ
                             │
                             ▼
                    Workflow Engine
                             │
                      ┌──────┴──────┐
                      │             │
                    DAG          Executor
                      │             │
                      └──────┬──────┘
                             ▼
                         RabbitMQ
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
             Worker 1     Worker 2     Worker 3
                │            │            │
                └────────────┼────────────┘
                             ▼
                         PostgreSQL