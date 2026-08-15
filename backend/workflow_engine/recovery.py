from backend.common.enums import (
    ExecutionStatus,
)

from backend.workflow_engine.checkpoint import (
    CheckpointManager,
)


class WorkflowRecovery:

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
    ):

        self.checkpoint_manager = (
            checkpoint_manager
        )

    def recover(
        self,
        workflow_run_id: str,
    ):

        context = self.checkpoint_manager.load(
            workflow_run_id
        )

        if context is None:

            raise ValueError(
                f"No checkpoint found for "
                f"workflow run: {workflow_run_id}"
            )

        if context.status in {
            ExecutionStatus.SUCCESS,
            ExecutionStatus.CANCELLED,
        }:

            return context

        context.status = ExecutionStatus.RUNNING

        return context