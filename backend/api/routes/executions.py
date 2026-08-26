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


router = APIRouter(
    prefix="/executions",
    tags=["Executions"],
)


executions: dict[
    str,
    dict[str, Any]
] = {}


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

    return execution


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