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

                         Module 9 

                                                  React
                           │
                         HTTP
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     Workflows         Executions       Schedules
          │                │                │
          ▼                ▼                ▼
     Compiler          Run State       Scheduler
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                       RabbitMQ
                           │
                           ▼
                   Workflow Engine
                           │
                           ▼
                        Workers

                        Module 10

                                                      React
                          /           \
                       REST          WebSocket
                        │                │
                        ▼                ▼
                    ┌────────────────────────┐
                    │        FastAPI         │
                    └───────────┬────────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
         Workflows          Executions         Scheduler
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                           RabbitMQ
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               Workflow      Workers     WebSocket
                Engine                    Bridge
                    │                       │
                    ▼                       ▼
                 Executor               Browsers
                    │
                    ▼
                 Workers
                    │
                    ▼
               PostgreSQL

               11th Module

                                          FLUXENGINE
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
          REST API          Scheduler         WebSocket
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                           RabbitMQ
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                    ▼          ▼          ▼
                Workflow     Workers   Event Bridge
                 Engine                   │
                    │                    ▼
                    │                  React
                    ▼
                 Executor
                    │
                    ▼
                  Tasks
                    │
                    ▼
               PostgreSQL
                    ▲
                    │
               Monitoring
                    │
             ┌──────┴──────┐
             ▼             ▼
          Metrics        Health
             │
             ▼
         Prometheus

         Module 12 

                             FluxEngine
                        │
                 Workflow Engine
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
      Task Started                Task Started
          │                           │
          ▼                           ▼
      Task Completed              Task Completed
          │                           │
          └─────────────┬─────────────┘
                        ▼
                 Workflow Completed
                        │
                        ▼
                  Prometheus

                  