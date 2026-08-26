from fastapi import FastAPI
from backend.api.websocket import router as websocket_router
from backend.api.routes import (
    health_router,
    workflow_router,
    execution_router,
    schedule_router,
)


app = FastAPI(
    title="FluxEngine API",
    description=(
        "Distributed Workflow Orchestration Engine"
    ),
    version="1.0.0",
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
    websocket_router
)

@app.get("/")
async def root():

    return {
        "name": "FluxEngine",
        "version": "1.0.0",
        "status": "running",
    }