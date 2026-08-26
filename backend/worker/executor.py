from typing import Any

from backend.event_bus.events import (
    TaskMessage,
    TaskResult,
)

from backend.worker.task_runner import (
    TaskRunner,
)


class WorkerExecutor:

    def __init__(
        self,
        worker_id: str,
        task_runner: TaskRunner,
    ):

        self.worker_id = worker_id

        self.task_runner = task_runner

    async def execute(
        self,
        task: TaskMessage,
    ) -> TaskResult:

        try:

            result = await self.task_runner.run(
                task.task_type,
                task.payload,
            )

            return TaskResult(
                task_run_id=task.task_run_id,

                workflow_run_id=task.workflow_run_id,

                task_id=task.task_id,

                worker_id=self.worker_id,

                success=True,

                result=result,
            )

        except Exception as exc:

            return TaskResult(
                task_run_id=task.task_run_id,

                workflow_run_id=task.workflow_run_id,

                task_id=task.task_id,

                worker_id=self.worker_id,

                success=False,

                error=str(exc),
            )