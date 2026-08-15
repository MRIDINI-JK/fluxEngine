from dataclasses import dataclass, field
from typing import Any

from backend.common.enums import ExecutionStatus, TaskStatus


@dataclass
class TaskExecution:
    task_id: str
    status: TaskStatus = TaskStatus.PENDING

    attempts: int = 0

    result: Any = None
    error: str | None = None


@dataclass
class ExecutionContext:

    workflow_run_id: str

    status: ExecutionStatus = ExecutionStatus.PENDING

    input_data: dict[str, Any] = field(
        default_factory=dict
    )

    outputs: dict[str, Any] = field(
        default_factory=dict
    )

    tasks: dict[str, TaskExecution] = field(
        default_factory=dict
    )

    error: str | None = None