import asyncio

from backend.websocket.manager import (
    ConnectionManager,
)


class WebSocketService:

    def __init__(
        self,
        manager: ConnectionManager,
    ):

        self.manager = manager

        self.queue: asyncio.Queue = (
            asyncio.Queue()
        )

        self.running = False

    async def publish(
        self,
        workflow_run_id: str,
        message: dict,
    ):

        await self.queue.put(
            (
                workflow_run_id,
                message,
            )
        )

    async def start(self):

        self.running = True

        while self.running:

            workflow_run_id, message = (
                await self.queue.get()
            )

            await self.manager.broadcast(
                workflow_run_id,
                message,
            )

            self.queue.task_done()

    def stop(self):

        self.running = False