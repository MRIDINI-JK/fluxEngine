from backend.common.enums import (
    ExecutionStatus,
    TaskStatus,
)


class InvalidStateTransition(Exception):
    pass


class ExecutionStateMachine:

    WORKFLOW_TRANSITIONS = {

        ExecutionStatus.PENDING: {
            ExecutionStatus.RUNNING,
            ExecutionStatus.CANCELLED,
        },

        ExecutionStatus.RUNNING: {
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        },

        ExecutionStatus.FAILED: {
            ExecutionStatus.RETRYING,
        },

        ExecutionStatus.RETRYING: {
            ExecutionStatus.RUNNING,
            ExecutionStatus.FAILED,
        },

        ExecutionStatus.SUCCESS: set(),

        ExecutionStatus.CANCELLED: set(),
    }

    TASK_TRANSITIONS = {

        TaskStatus.PENDING: {
            TaskStatus.READY,
            TaskStatus.SKIPPED,
        },

        TaskStatus.READY: {
            TaskStatus.RUNNING,
            TaskStatus.SKIPPED,
        },

        TaskStatus.RUNNING: {
            TaskStatus.SUCCESS,
            TaskStatus.FAILED,
        },

        TaskStatus.FAILED: {
            TaskStatus.RETRYING,
        },

        TaskStatus.RETRYING: {
            TaskStatus.READY,
            TaskStatus.FAILED,
        },

        TaskStatus.SUCCESS: set(),

        TaskStatus.SKIPPED: set(),
    }

    @classmethod
    def transition_workflow(
        cls,
        current: ExecutionStatus,
        target: ExecutionStatus,
    ):

        allowed = cls.WORKFLOW_TRANSITIONS.get(
            current,
            set(),
        )

        if target not in allowed:

            raise InvalidStateTransition(
                f"Invalid workflow transition: "
                f"{current} -> {target}"
            )

        return target

    @classmethod
    def transition_task(
        cls,
        current: TaskStatus,
        target: TaskStatus,
    ):

        allowed = cls.TASK_TRANSITIONS.get(
            current,
            set(),
        )

        if target not in allowed:

            raise InvalidStateTransition(
                f"Invalid task transition: "
                f"{current} -> {target}"
            )

        return target