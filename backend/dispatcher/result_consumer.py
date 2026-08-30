import asyncio

from backend.common.logger import logger

from backend.event_bus import RabbitMQ

from backend.event_bus.events import (
    TaskResult,
)

from backend.event_bus.routing import (
    RESULT_QUEUE,
)


class TaskResultConsumer:

    def __init__(
        self,
        rabbitmq: RabbitMQ,
    ):

        self.rabbitmq = rabbitmq

        self._task = None

    async def start(self):

        if self.rabbitmq.channel is None:
            raise RuntimeError(
                "RabbitMQ channel unavailable"
            )

        if self.rabbitmq.task_exchange is None:
            raise RuntimeError(
                "Task exchange unavailable"
            )

        queue = await (
            self.rabbitmq.channel.declare_queue(
                RESULT_QUEUE,
                durable=True,
            )
        )

        await queue.bind(
            self.rabbitmq.task_exchange,
            routing_key="result",
        )

        logger.info(
            "Task result consumer started"
        )

        self._task = asyncio.create_task(
            self._consume(queue)
        )

    async def _consume(
        self,
        queue,
    ):

        async with queue.iterator() as iterator:

            async for message in iterator:

                async with message.process():

                    result = (
                        TaskResult.model_validate_json(
                            message.body
                        )
                    )

                    logger.info(
                        f"Task result received: "
                        f"{result.task_id}"
                    )

                    logger.info(
                        f"Success: "
                        f"{result.success}"
                    )

                    logger.info(
                        f"Worker: "
                        f"{result.worker_id}"
                    )

                    if result.success:

                        logger.info(
                            f"Task completed: "
                            f"{result.task_id}"
                        )

                    else:

                        logger.error(
                            f"Task failed: "
                            f"{result.task_id} "
                            f"error={result.error}"
                        )

    async def stop(self):

        if self._task:

            self._task.cancel()

            await asyncio.gather(
                self._task,
                return_exceptions=True,
            )

            self._task = None