import asyncio

from backend.dispatcher.result_consumer import (
    TaskResultConsumer,
)

from backend.event_bus import RabbitMQ


async def main():

    print(
        "Starting task result consumer test..."
    )

    rabbitmq = RabbitMQ()

    await rabbitmq.connect()

    consumer = TaskResultConsumer(
        rabbitmq
    )

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