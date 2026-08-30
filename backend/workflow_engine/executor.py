import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
import time
from backend.common.enums import (
    ExecutionStatus,
    TaskStatus,
)

from backend.monitoring.metrics import (
    WORKFLOWS_STARTED,
    WORKFLOWS_COMPLETED,
    WORKFLOWS_FAILED,
    WORKFLOWS_RUNNING,
    WORKFLOW_DURATION,
)

from backend.workflow_engine.compiler import (
    CompiledWorkflow,
)

from backend.workflow_engine.context import (
    ExecutionContext,
    TaskExecution,
)

from backend.workflow_engine.state_machine import (
    ExecutionStateMachine,
)

from backend.workflow_engine.checkpoint import (
    CheckpointManager,
)

from backend.workflow_engine.retry import (
    RetryPolicy,
)


TaskHandler = Callable[
    [dict[str, Any]],
    Awaitable[Any],
]


class WorkflowExecutor:

    def __init__(
        self,
        checkpoint_manager: CheckpointManager | None = None,
        retry_policy: RetryPolicy | None = None,
    ):

        self.checkpoint_manager = (
            checkpoint_manager
            or CheckpointManager()
        )

        self.retry_policy = (
            retry_policy
            or RetryPolicy()
        )

        self.handlers: dict[
            str,
            TaskHandler
        ] = {}

    def register_handler(
        self,
        task_type: str,
        handler: TaskHandler,
    ):

        self.handlers[task_type] = handler

    async def execute(
        self,
        workflow: CompiledWorkflow,
        workflow_run_id: str,
        input_data: dict[str, Any] | None = None,
    ):
        # print("========== WORKFLOW EXECUTOR ENTERED ==========")
        # print("WORKFLOW RUN ID:", workflow_run_id)

        context = ExecutionContext(
            workflow_run_id=workflow_run_id,
            input_data=input_data or {},
        )
        print(
    "WORKFLOW EXECUTOR CALLED:",
    workflow_run_id,
)
        WORKFLOWS_STARTED.inc()
        # print(
    # "WORKFLOW STARTED METRIC:",
    # WORKFLOWS_STARTED._value.get(),
# )
        WORKFLOWS_RUNNING.inc()

        start_time = time.perf_counter()

        # Initialize task state
        for node in workflow.graph.nodes.values():

            if node.node_type in {
                "start",
                "end",
            }:
                continue

            context.tasks[node.id] = TaskExecution(
                task_id=node.id
            )

        context.status = (
            ExecutionStateMachine.transition_workflow(
                context.status,
                ExecutionStatus.RUNNING,
            )
        )

        self.checkpoint_manager.save(context)

        try:

            await self._run_workflow(
                workflow,
                context,
            )

            context.status = (
                ExecutionStateMachine.transition_workflow(
                    context.status,
                    ExecutionStatus.SUCCESS,
                )
            )
            WORKFLOWS_COMPLETED.inc()
#             print(
#     "WORKFLOW COMPLETED METRIC:",
#     WORKFLOWS_COMPLETED._value.get(),
# )
        except Exception as exc:

            context.error = str(exc)

            context.status = (
                ExecutionStateMachine.transition_workflow(
                    context.status,
                    ExecutionStatus.FAILED,
                )
            )
            WORKFLOWS_FAILED.inc()
            self.checkpoint_manager.save(context)

            raise
        finally:

            duration = (
            time.perf_counter()
            - start_time
    )

            WORKFLOW_DURATION.observe(
        duration
    )

            WORKFLOWS_RUNNING.dec()

        self.checkpoint_manager.save(context)

        return context

    async def _run_workflow(
        self,
        workflow: CompiledWorkflow,
        context: ExecutionContext,
    ):

        while True:

            ready_tasks = self._find_ready_tasks(
                workflow,
                context,
            )

            if not ready_tasks:

                if self._all_tasks_complete(
                    context
                ):
                    return

                raise RuntimeError(
                    "Workflow is blocked. "
                    "No ready tasks remain."
                )

            for task_id in ready_tasks:

                await self._execute_task(
                    workflow,
                    context,
                    task_id,
                )

                self.checkpoint_manager.save(
                    context
                )

    def _find_ready_tasks(
        self,
        workflow: CompiledWorkflow,
        context: ExecutionContext,
    ) -> list[str]:

        ready = []

        for node_id, task in context.tasks.items():

            if task.status != TaskStatus.PENDING:
                continue

            node = workflow.graph.get_node(
                node_id
            )

            dependencies_complete = all(
                context.tasks[dependency].status
                == TaskStatus.SUCCESS
                for dependency
                in node.dependencies
                if dependency in context.tasks
            )

            if dependencies_complete:

                task.status = (
                    ExecutionStateMachine.transition_task(
                        task.status,
                        TaskStatus.READY,
                    )
                )

                ready.append(node_id)

        return ready

    async def _execute_task(
        self,
        workflow: CompiledWorkflow,
        context: ExecutionContext,
        task_id: str,
    ):

        task = context.tasks[task_id]

        task.status = (
            ExecutionStateMachine.transition_task(
                task.status,
                TaskStatus.RUNNING,
            )
        )

        task.attempts += 1

        node = workflow.graph.get_node(
            task_id
        )

        handler = self.handlers.get(
            node.node_type
        )

        if handler is None:

            raise RuntimeError(
                f"No handler registered for "
                f"task type: {node.node_type}"
            )

        try:

            result = await handler(
                {
                    "workflow_run_id":
                        context.workflow_run_id,

                    "task_id":
                        task_id,

                    "input":
                        context.input_data,

                    "outputs":
                        context.outputs,

                    "config":
                        node.config,
                }
            )

            task.result = result

            task.status = (
                ExecutionStateMachine.transition_task(
                    task.status,
                    TaskStatus.SUCCESS,
                )
            )

            context.outputs[
                task_id
            ] = result

        except Exception as exc:

            task.error = str(exc)

            if self.retry_policy.should_retry(
                task.attempts
            ):

                task.status = (
                    ExecutionStateMachine.transition_task(
                        task.status,
                        TaskStatus.FAILED,
                    )
                )

                task.status = (
                    ExecutionStateMachine.transition_task(
                        task.status,
                        TaskStatus.RETRYING,
                    )
                )

                delay = (
                    self.retry_policy.get_delay(
                        task.attempts
                    )
                )

                await asyncio.sleep(delay)

                task.status = (
                    ExecutionStateMachine.transition_task(
                        task.status,
                        TaskStatus.READY,
                    )
                )

                await self._execute_task(
                    workflow,
                    context,
                    task_id,
                )

            else:

                task.status = (
                    ExecutionStateMachine.transition_task(
                        task.status,
                        TaskStatus.FAILED,
                    )
                )

                raise

    def _all_tasks_complete(
        self,
        context: ExecutionContext,
    ) -> bool:

        return all(
            task.status
            in {
                TaskStatus.SUCCESS,
                TaskStatus.SKIPPED,
            }
            for task in context.tasks.values()
        )