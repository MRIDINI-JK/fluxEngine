import asyncio

from backend.event_bus.events import TaskResult


class TaskResultStore:

    def __init__(self):

        self.results: dict[
            str,
            TaskResult
        ] = {}

        self.events: dict[
            str,
            asyncio.Event
        ] = {}

    def create_waiter(
        self,
        task_run_id: str,
    ):

        if task_run_id not in self.events:

            self.events[
                task_run_id
            ] = asyncio.Event()

    def set_result(
        self,
        result: TaskResult,
    ):

        self.results[
            result.task_run_id
        ] = result

        event = self.events.get(
            result.task_run_id
        )

        if event:

            event.set()

    async def wait_for_result(
        self,
        task_run_id: str,
        timeout: float = 60,
    ) -> TaskResult:

        self.create_waiter(
            task_run_id
        )

        event = self.events[
            task_run_id
        ]

        await asyncio.wait_for(
            event.wait(),
            timeout=timeout,
        )

        return self.results[
            task_run_id
        ]