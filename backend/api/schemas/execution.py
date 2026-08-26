from typing import Any

from pydantic import BaseModel


class ExecutionCreate(BaseModel):

    input_data: dict[str, Any] = {}


class ExecutionResponse(BaseModel):

    workflow_run_id: str

    workflow_id: int

    status: str

    input_data: dict[str, Any]

    outputs: dict[str, Any] = {}