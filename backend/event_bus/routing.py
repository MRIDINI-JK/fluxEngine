from backend.event_bus.events import EventType


EXCHANGE_NAME = "flux.events"


WORKFLOW_QUEUE = "flux.workflow"

WORKER_QUEUE = "flux.worker"

SCHEDULER_QUEUE = "flux.scheduler"


ROUTING_KEYS = {
    EventType.WORKFLOW_STARTED: "workflow.started",
    EventType.WORKFLOW_COMPLETED: "workflow.completed",
    EventType.WORKFLOW_FAILED: "workflow.failed",
    EventType.WORKFLOW_CANCELLED: "workflow.cancelled",

    EventType.TASK_DISPATCHED: "task.dispatched",
    EventType.TASK_STARTED: "task.started",
    EventType.TASK_COMPLETED: "task.completed",
    EventType.TASK_FAILED: "task.failed",

    EventType.WORKER_REGISTERED: "worker.registered",
    EventType.WORKER_HEARTBEAT: "worker.heartbeat",
    EventType.WORKER_OFFLINE: "worker.offline",
}