from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ScheduledJob:

    job_id: str

    workflow_id: int

    name: str

    cron_expression: str | None = None

    run_at: datetime | None = None

    enabled: bool = True

    input_data: dict[str, Any] = field(
        default_factory=dict
    )

