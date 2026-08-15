from copy import deepcopy

from backend.workflow_engine.context import (
    ExecutionContext,
)


class CheckpointManager:

    def __init__(self):

        self._checkpoints: dict[
            str,
            ExecutionContext
        ] = {}

    def save(
        self,
        context: ExecutionContext,
    ):

        self._checkpoints[
            context.workflow_run_id
        ] = deepcopy(context)

    def load(
        self,
        workflow_run_id: str,
    ) -> ExecutionContext | None:

        checkpoint = self._checkpoints.get(
            workflow_run_id
        )

        if checkpoint is None:
            return None

        return deepcopy(checkpoint)

    def delete(
        self,
        workflow_run_id: str,
    ):

        self._checkpoints.pop(
            workflow_run_id,
            None,
        )