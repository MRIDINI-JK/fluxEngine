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
from backend.dispatcher.dispatcher import TaskDispatcher

from backend.api.websocket import (
    router as websocket_router,
)

from backend.event_bus import RabbitMQ

from backend.monitoring import (
    TaskMonitor,
    WorkerMonitor,
)

from backend.dispatcher.result_store import (
    TaskResultStore,
)

from backend.dispatcher.result_consumer import (
    TaskResultConsumer,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # ==========================================
    # 1. Connect to RabbitMQ
    # ==========================================

    print("1. Connecting to RabbitMQ...")

    rabbitmq = RabbitMQ()
    await rabbitmq.connect()

    print("2. RabbitMQ connected")


    # ==========================================
    # 2. Create monitors
    # ==========================================

    worker_monitor = WorkerMonitor(
        rabbitmq
    )
    
    task_monitor = TaskMonitor(
        rabbitmq
    )
    task_dispatcher = TaskDispatcher(
        rabbitmq=rabbitmq,
        worker_monitor=worker_monitor,
    )

    # ==========================================
    # 3. Create ResultStore
    # ==========================================

    result_store = TaskResultStore()


    # ==========================================
    # 4. Create ResultConsumer
    # ==========================================

    result_consumer = TaskResultConsumer(
        rabbitmq=rabbitmq,
        result_store=result_store,
        worker_monitor=worker_monitor,
    )


    # ==========================================
    # 5. Save shared components in app.state
    # ==========================================

    app.state.rabbitmq = rabbitmq
    app.state.worker_monitor = worker_monitor
    app.state.task_monitor = task_monitor
    app.state.task_dispatcher = task_dispatcher
    app.state.result_store = result_store
    app.state.result_consumer = result_consumer


    # ==========================================
    # 6. Start background services
    # ==========================================

    print("3. Starting WorkerMonitor...")

    await worker_monitor.start()

    await task_monitor.start()

    await result_consumer.start()

    print("4. Background services started")


    # ==========================================
    # 7. API is running
    # ==========================================

    yield


    # ==========================================
    # 8. Shutdown
    # ==========================================

    print("5. Shutting down...")

    await result_consumer.stop()

    await worker_monitor.consumer.stop()

    await rabbitmq.close()

    print("6. RabbitMQ closed")


app = FastAPI(
    title="FluxEngine API",
    description="Distributed Workflow Orchestration Engine",
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================
# Routes
# ==========================================

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