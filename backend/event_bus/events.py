from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_CANCELLED = "workflow.cancelled"

    TASK_DISPATCHED = "task.dispatched"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    WORKER_REGISTERED = "worker.registered"
    WORKER_HEARTBEAT = "worker.heartbeat"
    WORKER_OFFLINE = "worker.offline"


class Event(BaseModel):
    event_id: str
    event_type: EventType

    source: str

    workflow_id: int | None = None
    workflow_run_id: int | None = None
    task_id: int | None = None
    task_run_id: int | None = None
    worker_id: int | None = None

    payload: dict = Field(default_factory=dict) 