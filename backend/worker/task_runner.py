from collections.abc import Awaitable, Callable
from typing import Any


TaskHandler = Callable[
    [dict[str, Any]],
    Awaitable[Any],
]


class TaskRunner:

    def __init__(self):

        self.handlers: dict[
            str,
            TaskHandler
        ] = {}

    def register(
        self,
        task_type: str,
        handler: TaskHandler,
    ):

        self.handlers[
            task_type
        ] = handler

    async def run(
        self,
        task_type: str,
        payload: dict[str, Any],
    ):

        handler = self.handlers.get(
            task_type
        )

        if handler is None:

            raise RuntimeError(
                f"No handler registered for "
                f"task type: {task_type}"
            )

        return await handler(payload)