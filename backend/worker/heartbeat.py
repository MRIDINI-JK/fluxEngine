import asyncio
from collections.abc import Awaitable, Callable


class WorkerHeartbeat:

    def __init__(
        self,
        worker_id: str,
        interval: float = 10.0,
    ):

        self.worker_id = worker_id

        self.interval = interval

        self.running = False

    async def start(
        self,
        callback: Callable[
            [str],
            Awaitable[None]
        ],
    ):

        self.running = True

        while self.running:

            await callback(
                self.worker_id
            )

            await asyncio.sleep(
                self.interval
            )

    def stop(self):

        self.running = False