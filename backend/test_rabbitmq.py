import asyncio

from backend.common.logger import logger
from backend.event_bus import RabbitMQ


async def main():

    rabbitmq = RabbitMQ()

    try:

        await rabbitmq.connect()

        logger.info(
            "RabbitMQ connection successful"
        )

    finally:

        await rabbitmq.close()


if __name__ == "__main__":
    asyncio.run(main())