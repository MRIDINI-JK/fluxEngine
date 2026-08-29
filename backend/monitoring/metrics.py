from prometheus_client import Counter, Gauge, Histogram


# --------------------------------------------------
# Workflow Metrics
# --------------------------------------------------

WORKFLOWS_STARTED = Counter(
    "fluxengine_workflows_started_total",
    "Total number of workflows started",
)

WORKFLOWS_COMPLETED = Counter(
    "fluxengine_workflows_completed_total",
    "Total number of workflows completed",
)

WORKFLOWS_FAILED = Counter(
    "fluxengine_workflows_failed_total",
    "Total number of workflows failed",
)

WORKFLOWS_RUNNING = Gauge(
    "fluxengine_workflows_running",
    "Number of workflows currently running",
)


WORKFLOW_DURATION = Histogram(
    "fluxengine_workflow_duration_seconds",
    "Workflow execution duration",
)


# --------------------------------------------------
# Task Metrics
# --------------------------------------------------

TASKS_STARTED = Counter(
    "fluxengine_tasks_started_total",
    "Total number of tasks started",
)

TASKS_COMPLETED = Counter(
    "fluxengine_tasks_completed_total",
    "Total number of tasks completed",
)

TASKS_FAILED = Counter(
    "fluxengine_tasks_failed_total",
    "Total number of tasks failed",
)

TASKS_RETRIED = Counter(
    "fluxengine_tasks_retried_total",
    "Total number of task retries",
)


TASK_DURATION = Histogram(
    "fluxengine_task_duration_seconds",
    "Task execution duration",
    buckets=(
        0.001,
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        float("inf"),
    ),
)


# --------------------------------------------------
# Worker Metrics
# --------------------------------------------------

WORKERS_REGISTERED = Gauge(
    "fluxengine_workers_registered",
    "Number of registered workers",
)

WORKERS_BUSY = Gauge(
    "fluxengine_workers_busy",
    "Number of busy workers",
)


# --------------------------------------------------
# RabbitMQ Metrics
# --------------------------------------------------

MESSAGES_PUBLISHED = Counter(
    "fluxengine_messages_published_total",
    "Total messages published",
)

MESSAGES_CONSUMED = Counter(
    "fluxengine_messages_consumed_total",
    "Total messages consumed",
)