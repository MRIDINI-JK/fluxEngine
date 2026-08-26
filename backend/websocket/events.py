from typing import Any

from pydantic import BaseModel, Field


class WebSocketEvent(BaseModel):

    event_type: str

    workflow_run_id: str

    task_id: str | None = None

    status: str | None = None

    data: dict[str, Any] = Field(
        default_factory=dict
    )