from aio_pika import (
    Channel,
    Exchange,
    ExchangeType,
    RobustConnection,
    connect_robust,
)

from backend.config import settings
from backend.event_bus.routing import EXCHANGE_NAME


class RabbitMQ:

    def __init__(self):
        self.connection: RobustConnection | None = None
        self.channel: Channel | None = None
        self.exchange: Exchange | None = None

    async def connect(self):

        self.connection = await connect_robust(
            settings.RABBITMQ_URL
        )

        self.channel = await self.connection.channel()

        await self.channel.set_qos(
            prefetch_count=10
        )

        self.exchange = await self.channel.declare_exchange(
            EXCHANGE_NAME,
            ExchangeType.TOPIC,
            durable=True
        )

        return self

    async def close(self):

        if self.connection:

            await self.connection.close()

            self.connection = None
            self.channel = None
            self.exchange = None