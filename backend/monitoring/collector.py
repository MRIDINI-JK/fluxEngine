from backend.monitoring.metrics import (
    WORKFLOWS_STARTED,
    WORKFLOWS_COMPLETED,
    WORKFLOWS_FAILED,
    WORKFLOWS_RUNNING,
    WORKFLOW_DURATION,
    TASKS_STARTED,
    TASKS_COMPLETED,
    TASKS_FAILED,
    TASKS_RETRIED,
    TASK_DURATION,
    WORKERS_REGISTERED,
    WORKERS_BUSY,
    MESSAGES_PUBLISHED,
    MESSAGES_CONSUMED,
)


class MetricsCollector:

    # ----------------------------------------------
    # Workflow
    # ----------------------------------------------

    def workflow_started(self):

        WORKFLOWS_STARTED.inc()

        WORKFLOWS_RUNNING.inc()

    def workflow_completed(
        self,
        duration: float | None = None,
    ):

        WORKFLOWS_COMPLETED.inc()

        WORKFLOWS_RUNNING.dec()

        if duration is not None:

            WORKFLOW_DURATION.observe(
                duration
            )

    def workflow_failed(
        self,
        duration: float | None = None,
    ):

        WORKFLOWS_FAILED.inc()

        WORKFLOWS_RUNNING.dec()

        if duration is not None:

            WORKFLOW_DURATION.observe(
                duration
            )

    # ----------------------------------------------
    # Tasks
    # ----------------------------------------------

    def task_started(self):

        TASKS_STARTED.inc()

    def task_completed(
        self,
        duration: float | None = None,
    ):

        TASKS_COMPLETED.inc()

        if duration is not None:

            TASK_DURATION.observe(
                duration
            )

    def task_failed(
        self,
        duration: float | None = None,
    ):

        TASKS_FAILED.inc()

        if duration is not None:

            TASK_DURATION.observe(
                duration
            )

    def task_retried(self):

        TASKS_RETRIED.inc()

    # ----------------------------------------------
    # Workers
    # ----------------------------------------------

    def workers_registered(
        self,
        count: int,
    ):

        WORKERS_REGISTERED.set(
            count
        )

    def workers_busy(
        self,
        count: int,
    ):

        WORKERS_BUSY.set(
            count
        )

    # ----------------------------------------------
    # RabbitMQ
    # ----------------------------------------------

    def message_published(self):

        MESSAGES_PUBLISHED.inc()

    def message_consumed(self):

        MESSAGES_CONSUMED.inc()