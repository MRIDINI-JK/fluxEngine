from typing import Any

from pydantic import BaseModel


class ScheduleCreate(BaseModel):

    workflow_id: int

    name: str

    cron_expression: str | None = None

    run_at: str | None = None

    enabled: bool = True

    input_data: dict[str, Any] = {}


class ScheduleResponse(BaseModel):

    job_id: str

    workflow_id: int

    name: str

    cron_expression: str | None

    run_at: str | None

    enabled: bool