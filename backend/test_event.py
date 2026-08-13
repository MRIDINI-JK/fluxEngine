import asyncio
import uuid

from backend.common.logger import logger

from backend.event_bus import (
    Event,
    EventProducer,
    EventType,
    RabbitMQ,
)


async def main():

    rabbitmq = RabbitMQ()

    await rabbitmq.connect()

    producer = EventProducer(rabbitmq)

    event = Event(
        event_id=str(uuid.uuid4()),

        event_type=EventType.WORKFLOW_STARTED,

        source="test",

        workflow_id=1,

        workflow_run_id=100,

        payload={
            "message": "Test workflow started"
        }
    )

    await producer.publish(event)

    logger.info(
        f"Published event: {event.event_type}"
    )

    await rabbitmq.close()


if __name__ == "__main__":
    asyncio.run(main())