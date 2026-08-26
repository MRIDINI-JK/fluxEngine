import asyncio
import socket
import uuid

from aio_pika import Message

from backend.common.logger import logger

from backend.event_bus import (
    RabbitMQ,
)

from backend.event_bus.events import (
    TaskMessage,
)

from backend.event_bus.routing import (
    WORKER_QUEUE,
    TASK_EXCHANGE_NAME,
)

from backend.worker.executor import (
    WorkerExecutor,
)

from backend.worker.registry import (
    WorkerInfo,
    WorkerRegistry,
)

from backend.worker.task_runner import (
    TaskRunner,
)


class Worker:

    def __init__(
        self,
        capabilities: set[str],
    ):

        self.worker_id = str(
            uuid.uuid4()
        )

        self.hostname = socket.gethostname()

        self.capabilities = capabilities

        self.rabbitmq = RabbitMQ()

        self.registry = WorkerRegistry()

        self.task_runner = TaskRunner()

        self.executor = WorkerExecutor(
            worker_id=self.worker_id,
            task_runner=self.task_runner,
        )

    async def start(self):

        await self.rabbitmq.connect()

        worker_info = WorkerInfo(
            worker_id=self.worker_id,

            hostname=self.hostname,

            capabilities=self.capabilities,
        )

        self.registry.register(
            worker_info
        )

        logger.info(
            f"Worker started: "
            f"{self.worker_id}"
        )

        logger.info(
            f"Capabilities: "
            f"{self.capabilities}"
        )

        await self._consume_tasks()

    async def _consume_tasks(self):

        channel = self.rabbitmq.channel

        task_exchange = (
            self.rabbitmq.task_exchange
        )

        if channel is None:
            raise RuntimeError(
                "RabbitMQ channel unavailable"
            )

        if task_exchange is None:
            raise RuntimeError(
                "Task exchange unavailable"
            )

        queue = await channel.declare_queue(
            WORKER_QUEUE,
            durable=True,
        )

        await queue.bind(
            task_exchange,
            routing_key="task",
        )

        logger.info(
            "Worker waiting for tasks..."
        )

        async with queue.iterator() as iterator:

            async for message in iterator:

                async with message.process():

                    task = (
                        TaskMessage.model_validate_json(
                            message.body
                        )
                    )

                    logger.info(
                        f"Received task: "
                        f"{task.task_id}"
                    )

                    result = (
                        await self.executor.execute(
                            task
                        )
                    )

                    await self._publish_result(
                        result
                    )

    async def _publish_result(
        self,
        result,
    ):

        if self.rabbitmq.task_exchange is None:

            raise RuntimeError(
                "Task exchange unavailable"
            )

        message = Message(
            body=result.model_dump_json().encode(
                "utf-8"
            ),

            content_type="application/json",

            message_id=result.task_run_id,
        )

        await self.rabbitmq.task_exchange.publish(
            message,
            routing_key="result",
        )

        logger.info(
            f"Published result for "
            f"{result.task_id}"
        )