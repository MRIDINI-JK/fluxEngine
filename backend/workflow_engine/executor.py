import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from backend.common.enums import (
    ExecutionStatus,
    TaskStatus,
)

from backend.event_bus.events import TaskMessage

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
        checkpoint_manager=None,
        retry_policy=None,
        task_dispatcher=None,
        result_store=None,
    ):

        self.checkpoint_manager = (
            checkpoint_manager
            or CheckpointManager()
        )

        self.retry_policy = (
            retry_policy
            or RetryPolicy()
        )

        self.task_dispatcher = task_dispatcher
        self.result_store = result_store

        # Kept for compatibility with the existing
        # local execution functionality.
        self.handlers: dict[
            str,
            TaskHandler,
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

        context = ExecutionContext(
            workflow_run_id=workflow_run_id,
            input_data=input_data or {},
        )

        print(
            "WORKFLOW EXECUTOR CALLED:",
            workflow_run_id,
        )

        WORKFLOWS_STARTED.inc()
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

        # ==========================================
        # 1. READY -> RUNNING
        # ==========================================

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

        # ==========================================
        # 2. Check distributed components
        # ==========================================

        if self.task_dispatcher is None:

            raise RuntimeError(
                "TaskDispatcher is not configured"
            )

        if self.result_store is None:

            raise RuntimeError(
                "TaskResultStore is not configured"
            )

        # ==========================================
        # 3. Create task run ID
        # ==========================================

        task_run_id = str(
            uuid.uuid4()
        )

        # ==========================================
        # 4. Build TaskMessage
        # ==========================================

        task_message = TaskMessage(
            task_run_id=task_run_id,
            workflow_run_id=context.workflow_run_id,
            task_id=task_id,
            task_type=node.node_type,
            payload={
                "input": context.input_data,
                "outputs": context.outputs,
                "config": node.config,
            },
        )

        print(
            f"Dispatching task: {task_id}"
        )

        # ==========================================
        # 5. Create waiter BEFORE dispatch
        # ==========================================

        self.result_store.create_waiter(
            task_run_id
        )

        # ==========================================
        # 6. Dispatch to worker
        # ==========================================

        worker = await self.task_dispatcher.dispatch(
            task_message
        )

        if worker is None:

            task.error = (
                f"No available worker for "
                f"task type: {node.node_type}"
            )

            task.status = (
                ExecutionStateMachine.transition_task(
                    task.status,
                    TaskStatus.FAILED,
                )
            )

            raise RuntimeError(
                task.error
            )

        print(
            f"Task dispatched: {task_id} "
            f"-> worker {worker['worker_id']}"
        )

        # ==========================================
        # 7. Wait for worker result
        # ==========================================

        try:

            result = (
                await self.result_store.wait_for_result(
                    task_run_id,
                    timeout=60,
                )
            )

        except asyncio.TimeoutError:

            task.error = (
                f"Task timed out waiting for result: "
                f"{task_id}"
            )

            task.status = (
                ExecutionStateMachine.transition_task(
                    task.status,
                    TaskStatus.FAILED,
                )
            )

            raise RuntimeError(
                task.error
            )

        # ==========================================
        # 8. Process result
        # ==========================================

        if result.success:

            task.result = result.result

            task.status = (
                ExecutionStateMachine.transition_task(
                    task.status,
                    TaskStatus.SUCCESS,
                )
            )

            context.outputs[
                task_id
            ] = result.result

            print(
                f"Distributed task completed: "
                f"{task_id}"
            )

        else:

            task.error = (
                result.error
                or "Task failed"
            )

            # ======================================
            # Retry
            # ======================================

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

                await asyncio.sleep(
                    delay
                )

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

                raise RuntimeError(
                    task.error
                )

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