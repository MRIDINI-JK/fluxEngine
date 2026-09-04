import asyncio
import uuid
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
)

from backend.api.schemas import (
    ExecutionCreate,
    ExecutionResponse,
)

from backend.api.routes.workflows import (
    workflows,
)

from backend.workflow_engine import (
    WorkflowCompiler,
    WorkflowExecutor,
)


router = APIRouter(
    prefix="/executions",
    tags=["Executions"],
)


executions: dict[
    str,
    dict[str, Any]
] = {}


compiler = WorkflowCompiler()


# ==========================================================
# Execute workflow
# ==========================================================

async def execute_workflow(
    workflow_id: int,
    workflow_run_id: str,
    input_data: dict[str, Any],
    task_dispatcher,
    result_store,
):

    execution = executions[
        workflow_run_id
    ]

    try:

        # --------------------------------------------------
        # Get workflow
        # --------------------------------------------------

        workflow_record = workflows[
            workflow_id
        ]

        workflow_definition = (
            workflow_record["definition"]
        )

        # --------------------------------------------------
        # Compile workflow
        # --------------------------------------------------

        compiled = compiler.compile(
            workflow_definition
        )

        # --------------------------------------------------
        # Create distributed executor
        # --------------------------------------------------

        executor = WorkflowExecutor(
            task_dispatcher=task_dispatcher,
            result_store=result_store,
        )

        execution["status"] = "RUNNING"

        print(
            f"Starting distributed workflow: "
            f"{workflow_run_id}"
        )

        # --------------------------------------------------
        # Execute
        # --------------------------------------------------

        context = await executor.execute(
            workflow=compiled,
            workflow_run_id=workflow_run_id,
            input_data=input_data,
        )

        # --------------------------------------------------
        # Update execution state
        # --------------------------------------------------

        execution["status"] = (
            context.status.value
            if hasattr(
                context.status,
                "value",
            )
            else str(
                context.status
            )
        )

        execution["outputs"] = (
            context.outputs
        )

        execution["error"] = (
            context.error
        )

        print(
            f"Workflow completed: "
            f"{workflow_run_id}"
        )

    except Exception as exc:

        execution["status"] = "FAILED"

        execution["error"] = str(
            exc
        )

        print(
            f"Workflow failed: "
            f"{workflow_run_id}: "
            f"{exc}"
        )


# ==========================================================
# Start workflow
# ==========================================================

@router.post(
    "/workflow/{workflow_id}",
    response_model=ExecutionResponse,
)
async def start_workflow(
    workflow_id: int,
    execution_data: ExecutionCreate,
    request: Request,
):

    # ------------------------------------------------------
    # Check workflow
    # ------------------------------------------------------

    workflow = workflows.get(
        workflow_id
    )

    if workflow is None:

        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    # ------------------------------------------------------
    # Get shared distributed services
    # ------------------------------------------------------

    task_dispatcher = (
        request.app.state.task_dispatcher
    )

    result_store = (
        request.app.state.result_store
    )

    # ------------------------------------------------------
    # Create workflow run
    # ------------------------------------------------------

    workflow_run_id = str(
        uuid.uuid4()
    )

    execution = {

        "workflow_run_id":
            workflow_run_id,

        "workflow_id":
            workflow_id,

        "status":
            "PENDING",

        "input_data":
            execution_data.input_data,

        "outputs":
            {},

        "error":
            None,
    }

    executions[
        workflow_run_id
    ] = execution

    # ------------------------------------------------------
    # Start workflow in background
    # ------------------------------------------------------

    asyncio.create_task(
        execute_workflow(
            workflow_id=workflow_id,

            workflow_run_id=workflow_run_id,

            input_data=(
                execution_data.input_data
            ),

            task_dispatcher=(
                task_dispatcher
            ),

            result_store=(
                result_store
            ),
        )
    )

    return execution


# ==========================================================
# Get execution
# ==========================================================

@router.get(
    "/{workflow_run_id}",
    response_model=ExecutionResponse,
)
async def get_execution(
    workflow_run_id: str,
):

    execution = executions.get(
        workflow_run_id
    )

    if execution is None:

        raise HTTPException(
            status_code=404,
            detail="Execution not found",
        )

    return execution


# ==========================================================
# Temporary dispatcher test
# ==========================================================

@router.post(
    "/test-dispatch"
)
async def test_dispatch(
    request: Request,
):

    dispatcher = (
        request.app.state.task_dispatcher
    )

    from backend.event_bus.events import (
        TaskMessage,
    )

    task = TaskMessage(
        task_run_id=str(
            uuid.uuid4()
        ),

        workflow_run_id=(
            "workflow-test-001"
        ),

        task_id="task_a",

        task_type="python",

        payload={
            "value": 21
        },
    )

    worker = await dispatcher.dispatch(
        task
    )

    if worker is None:

        raise HTTPException(
            status_code=503,
            detail="No available worker",
        )

    return {

        "status":
            "dispatched",

        "task_run_id":
            task.task_run_id,

        "task_id":
            task.task_id,

        "worker_id":
            worker["worker_id"],
    }