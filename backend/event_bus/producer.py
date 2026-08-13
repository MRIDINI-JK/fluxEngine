from aio_pika import DeliveryMode, Message

from backend.event_bus.events import Event
from backend.event_bus.rabbitmq import RabbitMQ
from backend.event_bus.routing import ROUTING_KEYS


class EventProducer:

    def __init__(self, rabbitmq: RabbitMQ):

        self.rabbitmq = rabbitmq

    async def publish(self, event: Event):

        if self.rabbitmq.exchange is None:
            raise RuntimeError(
                "RabbitMQ is not connected"
            )

        routing_key = ROUTING_KEYS[event.event_type]

        message = Message(
            body=event.model_dump_json().encode("utf-8"),

            content_type="application/json",

            delivery_mode=DeliveryMode.PERSISTENT,

            message_id=event.event_id,
        )

        await self.rabbitmq.exchange.publish(
            message,
            routing_key=routing_key
        )