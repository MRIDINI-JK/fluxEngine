import asyncio
from collections.abc import Awaitable, Callable

from backend.event_bus.events import Event
from backend.event_bus.rabbitmq import RabbitMQ


EventHandler = Callable[[Event], Awaitable[None]]


class EventConsumer:

    def __init__(self, rabbitmq: RabbitMQ):

        self.rabbitmq = rabbitmq
        self._tasks: list[asyncio.Task] = []

    async def subscribe(
        self,
        queue_name: str,
        routing_keys: list[str],
        handler: EventHandler,
    ):

        if self.rabbitmq.channel is None:
            raise RuntimeError(
                "RabbitMQ is not connected"
            )

        if self.rabbitmq.exchange is None:
            raise RuntimeError(
                "RabbitMQ exchange is not initialized"
            )

        queue = await self.rabbitmq.channel.declare_queue(
            queue_name,
            durable=True,
        )

        for routing_key in routing_keys:

            await queue.bind(
                self.rabbitmq.exchange,
                routing_key=routing_key,
            )

        task = asyncio.create_task(
            self._consume(
                queue,
                handler,
            )
        )

        self._tasks.append(task)

    async def _consume(
        self,
        queue,
        handler: EventHandler,
    ):

        async with queue.iterator() as queue_iterator:

            async for message in queue_iterator:

                async with message.process():

                    event = Event.model_validate_json(
                        message.body
                    )

                    await handler(event)

    async def stop(self):

        for task in self._tasks:

            task.cancel()

        if self._tasks:

            await asyncio.gather(
                *self._tasks,
                return_exceptions=True,
            )

        self._tasks.clear()