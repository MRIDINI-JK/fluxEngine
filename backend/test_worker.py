import asyncio

from backend.common.logger import logger

from backend.worker import (
    TaskRunner,
    Worker,
)


async def python_task(payload):

    value = payload["value"]

    logger.info(
        f"Running python task with value={value}"
    )

    return value * 2


async def main():

    worker = Worker(
        capabilities={
            "python"
        }
    )

    worker.task_runner.register(
        "python",
        python_task,
    )

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())