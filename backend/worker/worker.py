import asyncio
import socket
import uuid
from datetime import datetime, timezone
from aio_pika import Message
from typing import Any

from backend.database.models import event
from backend.database.models import event
import time
from backend.common.logger import logger
from backend.database.models import event
from backend.database.models import event
from backend.event_bus import (
    Event,
    EventType,
)

# from backend.monitoring.metrics import (
#     TASKS_STARTED,
#     TASKS_COMPLETED,
#     TASKS_FAILED,
#     TASKS_RETRIED,
#     TASK_DURATION,
# )
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
        self.task_runner.register(
                "python",
            self.python_task,
)
        self.heartbeat_task = None
        self.busy = False
    async def python_task(
    self,
    payload: dict[str, Any],
):
        logger.info(f"FULL TASK PAYLOAD: {payload}")

        input_data = payload.get("input", {})
        outputs = payload.get("outputs", {})
        config = payload.get("config", {})

        value = input_data.get("value", 0)

        logger.info(f"Running python task with value={value}")
        logger.info(f"Previous outputs: {outputs}")
        logger.info(f"Task config: {config}")

        function = config.get("function")

        if function == "process_a":
            result = value * 2

        elif function == "process_b":
            previous_result = outputs.get("task_a", 0)
            result = previous_result + 10

        else:
            result = value

        logger.info(f"Task result: {result}")

        return result

    async def start(self):

        await self.rabbitmq.connect()

        await self._register_worker()

        self.heartbeat_task = asyncio.create_task(
        self._heartbeat_loop()
    )

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

                    logger.info(
                    f"Task started: "
                    f"{task.task_id}"
)

                    self.busy = True

                    start_time = time.perf_counter()

                    await self._publish_task_event(
                    EventType.TASK_STARTED,
                    task,
)

                    try:

                        result = await self.executor.execute(
                            task
    )

                        duration = (
                time.perf_counter()
        - start_time
    )

                        if result.success:

                            await self._publish_task_event(
                        EventType.TASK_COMPLETED,
                task,
                        result=result,
                        duration=duration,
        )

                        else:

                            await self._publish_task_event(
                    EventType.TASK_FAILED,
                    task,
                    result=result,
                    duration=duration,
        )

                        logger.info(
        f"Task completed: "
        f"{task.task_id} "
        f"success={result.success} "
        f"attempts={result.attempts}"
    )

                    finally:

                        self.busy = False

                    await self._publish_result(
    result
)
    async def _publish_task_event(
    self,
    event_type,
    task,
    result=None,
    duration=None,
):

        if self.rabbitmq.exchange is None:

            raise RuntimeError(
            "RabbitMQ exchange unavailable"
        )

        payload = {
        "task_id": task.task_id,
        "workflow_run_id": task.workflow_run_id,
    }

        if result is not None:

            payload.update({
            "success": result.success,
            "attempts": result.attempts,
            "result": result.result,
            "error": result.error,
        })

        if duration is not None:

            payload["duration"] = duration

        event = Event(
            event_id=str(uuid.uuid4()),

        event_type=event_type,

        source="worker",

        payload=payload,
    )

        message = Message(
        body=event.model_dump_json().encode(
            "utf-8"
        ),

        content_type="application/json",

        message_id=event.event_id,
    )

        await self.rabbitmq.exchange.publish(
        message,

        routing_key=event_type.value,
    )

        logger.info(
        f"Published event: "
        f"{event_type.value} "
        f"task={task.task_id}"
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
    async def _register_worker(self):

        if self.rabbitmq.exchange is None:
            raise RuntimeError(
                "RabbitMQ exchange unavailable"
            )

        event = Event(
            event_id=str(uuid.uuid4()),

            event_type=(
                    EventType.WORKER_REGISTERED
                ),

            source="worker",

            payload={
            "worker_id": self.worker_id,

            "hostname": self.hostname,

            "capabilities": list(
                self.capabilities
            ),
            "busy": self.busy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

        message = Message(
            body=event.model_dump_json().encode(
                "utf-8"
            ),

            content_type="application/json",

            message_id=event.event_id,
        )

        await self.rabbitmq.exchange.publish(
            message,
            routing_key=(
                EventType.WORKER_REGISTERED.value
        ),
        )

        logger.info(
            f"Worker registration event "
            f"published: {self.worker_id}"
        )
    async def _heartbeat_loop(self):

        while True:

            try:

                await self._publish_heartbeat()

                await asyncio.sleep(10)

            except asyncio.CancelledError:

                logger.info(
                    "Worker heartbeat stopped"
            )

                break

            except Exception as exc:

                logger.error(
                    f"Heartbeat failed: {exc}"
            )

                await asyncio.sleep(10)
    async def _publish_heartbeat(self):

        if self.rabbitmq.exchange is None:

            raise RuntimeError(
                "RabbitMQ exchange unavailable"
            )

        event = Event(
            event_id=str(uuid.uuid4()),

            event_type=(
                EventType.WORKER_HEARTBEAT
        ),

            source="worker",

            payload={
                "worker_id": self.worker_id,

                "hostname": self.hostname,

                "capabilities": list(
                    self.capabilities
            ),
               

                "busy": self.busy,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),

        },
    )

        message = Message(
            body=event.model_dump_json().encode(
                "utf-8"
        ),

            content_type="application/json",

            message_id=event.event_id,
    )

        await self.rabbitmq.exchange.publish(
            message,

            routing_key=(
                EventType.WORKER_HEARTBEAT.value
        ),
    )

        logger.info(
            f"Worker heartbeat: "
            f"{self.worker_id}"
    )

async def main():

    worker = Worker(
            capabilities={
                "python"
        }
    )

    await worker.start()


if __name__ == "__main__":

    asyncio.run(main())