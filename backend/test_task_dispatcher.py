import asyncio
import uuid

from backend.dispatcher.dispatcher import (
    TaskDispatcher,
)

from backend.event_bus import RabbitMQ

from backend.event_bus.events import (
    TaskMessage,
)

from backend.worker.registry import (
    WorkerInfo,
    WorkerRegistry,
)


async def main():

    print(
        "Starting task dispatcher test..."
    )

    rabbitmq = RabbitMQ()

    await rabbitmq.connect()

    registry = WorkerRegistry()

    worker = WorkerInfo(
        worker_id=str(uuid.uuid4()),

        hostname="test-worker",

        capabilities={
            "python"
        },
    )

    registry.register(
        worker
    )

    dispatcher = TaskDispatcher(
        rabbitmq=rabbitmq,

        registry=registry,
    )

    task = TaskMessage(

        task_run_id=str(
            uuid.uuid4()
        ),

        workflow_run_id=str(
            uuid.uuid4()
        ),

        task_id="task_a",

        task_type="python",

        payload={
            "value": 21
        },
    )

    selected_worker = (
        await dispatcher.dispatch(
            task
        )
    )

    if selected_worker:

        print(
            "Task dispatched successfully!"
        )

        print(
            "Worker:",
            selected_worker.worker_id
        )

        print(
            "Busy:",
            selected_worker.busy
        )

    else:

        print(
            "No worker available"
        )

    await rabbitmq.close()


if __name__ == "__main__":

    asyncio.run(main())