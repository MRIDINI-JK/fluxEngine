import uuid
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
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


async def execute_workflow(
    workflow_id: int,
    workflow_run_id: str,
    input_data: dict[str, Any],
):

    execution = executions[
        workflow_run_id
    ]

    try:
        workflow_record = workflows[
    workflow_id
]
        workflow_definition = workflow_record[
            "definition"
        ]

        compiled = compiler.compile(
            workflow_definition
        )

        executor = WorkflowExecutor()

        async def python_handler(data):

            print(
                f"Executing task: "
                f"{data['task_id']}"
            )

            return {
                "task_id":
                    data["task_id"],

                "message":
                    "Task completed",

                "input":
                    data["input"],
            }

        executor.register_handler(
            "python",
            python_handler,
        )

        execution["status"] = "RUNNING"

        context = await executor.execute(
            workflow=compiled,

            workflow_run_id=workflow_run_id,

            input_data=input_data,
        )

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


@router.post(
    "/workflow/{workflow_id}",
    response_model=ExecutionResponse,
)
async def start_workflow(
    workflow_id: int,
    request: ExecutionCreate,
):

    workflow = workflows.get(
        workflow_id
    )

    if workflow is None:

        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

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
            request.input_data,

        "outputs":
            {},
    }

    executions[
        workflow_run_id
    ] = execution

    await execute_workflow(
        workflow_id=workflow_id,

        workflow_run_id=workflow_run_id,

        input_data=request.input_data,
    )

    return executions[
        workflow_run_id
    ]


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