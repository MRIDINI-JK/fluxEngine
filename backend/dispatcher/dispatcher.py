from aio_pika import Message

from backend.common.logger import logger

from backend.event_bus import RabbitMQ

from backend.event_bus.events import (
    TaskMessage,
)


class TaskDispatcher:

    def __init__(
        self,
        rabbitmq: RabbitMQ,
        worker_monitor,
    ):

        self.rabbitmq = rabbitmq

        self.worker_monitor = worker_monitor

    def find_worker(
        self,
        task_type: str,
    ):

        workers = (
            self.worker_monitor.get_workers()
        )

        for worker in workers:

            capabilities = worker.get(
                "capabilities",
                [],
            )

            busy = worker.get(
                "busy",
                False,
            )

            if (
                task_type in capabilities
                and not busy
            ):

                return worker

        return None

    async def dispatch(
        self,
        task: TaskMessage,
    ):

        worker = self.find_worker(
            task.task_type
        )

        if worker is None:

            logger.warning(
                f"No available worker for "
                f"task type: {task.task_type}"
            )

            return None

        if self.rabbitmq.task_exchange is None:

            raise RuntimeError(
                "Task exchange unavailable"
            )

        message = Message(
            body=task.model_dump_json().encode(
                "utf-8"
            ),

            content_type="application/json",

            message_id=task.task_run_id,
        )

        await self.rabbitmq.task_exchange.publish(
            message,

            routing_key="task",
        )

        worker["busy"] = True

        logger.info(
            f"Task dispatched: "
            f"{task.task_id} "
            f"-> worker "
            f"{worker['worker_id']}"
        )

        return worker