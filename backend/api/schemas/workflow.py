from typing import Any

from pydantic import BaseModel, Field


class WorkflowCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    version: int = 1

    definition: dict[str, Any]


class WorkflowResponse(BaseModel):

    id: int

    name: str

    version: int

    definition: dict[str, Any]