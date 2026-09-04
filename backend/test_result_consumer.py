import asyncio

from backend.dispatcher.result_consumer import (
    TaskResultConsumer,
)
from backend.dispatcher.result_store import (
    TaskResultStore,
)
from backend.event_bus import RabbitMQ, rabbitmq


async def main():

    print(
        "Starting task result consumer test..."
    )

    rabbitmq = RabbitMQ()

    await rabbitmq.connect()
    result_store = TaskResultStore()

    consumer = TaskResultConsumer(
    rabbitmq,
    result_store,
)

    # consumer = TaskResultConsumer(
    #     rabbitmq
    # )

    await consumer.start()

    print(
        "Waiting for task results..."
    )

    try:

        while True:

            await asyncio.sleep(1)

    except KeyboardInterrupt:

        print(
            "Stopping result consumer..."
        )

    finally:

        await consumer.stop()

        await rabbitmq.close()


if __name__ == "__main__":

    asyncio.run(main())