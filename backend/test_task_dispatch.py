import asyncio
import uuid

from aio_pika import Message

from backend.event_bus import RabbitMQ


async def main():

    rabbitmq = RabbitMQ()

    await rabbitmq.connect()

    task = {
        "task_run_id": str(uuid.uuid4()),

        "workflow_run_id": "workflow-001",

        "task_id": "task_a",

        "task_type": "python",

        "payload": {
            "value": 21
        }
    }

    message = Message(
        body=(
            __import__("json")
            .dumps(task)
            .encode("utf-8")
        ),

        content_type="application/json",
    )

    await rabbitmq.task_exchange.publish(
        message,
        routing_key="task",
    )

    print("Task dispatched")

    await rabbitmq.close()


if __name__ == "__main__":
    asyncio.run(main())