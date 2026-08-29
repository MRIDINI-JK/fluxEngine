from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import (
    health_router,
    workflow_router,
    execution_router,
    schedule_router,
    monitoring_router,
    worker_router,
)


from backend.monitoring import (
    TaskMonitor,
)

from backend.api.websocket import (
    router as websocket_router,
)

from backend.event_bus import RabbitMQ

from backend.monitoring import (
    WorkerMonitor,
)


rabbitmq = RabbitMQ()


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("1. Connecting to RabbitMQ...")
    rabbitmq = RabbitMQ()
    await rabbitmq.connect()

    print("2. RabbitMQ connected")

    worker_monitor = WorkerMonitor(
        rabbitmq    
    )

    task_monitor = TaskMonitor(
        rabbitmq
    )

    app.state.rabbitmq = rabbitmq
    app.state.worker_monitor = worker_monitor
    app.state.task_monitor = task_monitor
    print("3. Starting WorkerMonitor...")

    await worker_monitor.start()
    await task_monitor.start()
    print("4. WorkerMonitor started")

    yield

    print("5. Closing RabbitMQ...")

    await rabbitmq.close()


app = FastAPI(
    title="FluxEngine API",
    description="Distributed Workflow Orchestration Engine",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(
    health_router
)

app.include_router(
    workflow_router
)

app.include_router(
    execution_router
)

app.include_router(
    schedule_router
)

app.include_router(
    monitoring_router
)

app.include_router(
    worker_router
)

app.include_router(
    websocket_router
)


@app.get("/")
async def root():

    return {
        "name": "FluxEngine",
        "version": "1.0.0",
        "status": "running",
    }