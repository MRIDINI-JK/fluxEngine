import asyncio

from backend.common.logger import logger

from backend.event_bus import (
    Event,
    EventConsumer,
    RabbitMQ,
)


async def handle_event(event: Event):

    logger.info(
        f"Received event: "
        f"{event.event_type}"
    )

    logger.info(
        f"Payload: {event.payload}"
    )


async def main():

    rabbitmq = RabbitMQ()

    await rabbitmq.connect()

    consumer = EventConsumer(rabbitmq)

    await consumer.subscribe(
        queue_name="flux.test",

        routing_keys=[
            "workflow.started"
        ],

        handler=handle_event,
    )


if __name__ == "__main__":
    asyncio.run(main())