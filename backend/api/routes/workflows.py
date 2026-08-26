from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.api.schemas import (
    WorkflowCreate,
    WorkflowResponse,
)

from backend.workflow_engine import (
    WorkflowCompiler,
    WorkflowValidationError,
)


router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


workflows: dict[int, dict[str, Any]] = {}

next_workflow_id = 1


@router.post(
    "",
    response_model=WorkflowResponse,
)
async def create_workflow(
    request: WorkflowCreate,
):

    global next_workflow_id

    compiler = WorkflowCompiler()

    try:

        compiler.compile(
            request.definition
        )

    except WorkflowValidationError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    workflow = {
        "id": next_workflow_id,

        "name": request.name,

        "version": request.version,

        "definition": request.definition,
    }

    workflows[
        next_workflow_id
    ] = workflow

    next_workflow_id += 1

    return workflow


@router.get(
    "",
    response_model=list[WorkflowResponse],
)
async def list_workflows():

    return list(
        workflows.values()
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
)
async def get_workflow(
    workflow_id: int,
):

    workflow = workflows.get(
        workflow_id
    )

    if workflow is None:

        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return workflow