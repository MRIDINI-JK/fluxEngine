import asyncio

from backend.api.websocket import manager


async def main():

    await manager.broadcast(
        "test-run-001",
        {
            "event_type": "task.completed",

            "workflow_run_id":
                "test-run-001",

            "task_id":
                "task_a",

            "status":
                "SUCCESS",

            "data": {
                "result": 42
            }
        }
    )


if __name__ == "__main__":

    asyncio.run(main())