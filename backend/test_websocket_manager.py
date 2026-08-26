import asyncio

from backend.websocket import (
    ConnectionManager,
)


class FakeWebSocket:

    def __init__(self):
        self.messages = []

    async def send_json(self, message):
        self.messages.append(message)


async def main():

    print("Starting WebSocket manager test...")

    manager = ConnectionManager()

    websocket = FakeWebSocket()

    print("Creating fake connection...")

    manager.connections[
        "run-001"
    ].add(websocket)

    print(
        "Connection count:",
        manager.connection_count("run-001"),
    )

    await manager.broadcast(
        "run-001",
        {
            "event_type": "task.completed",
            "workflow_run_id": "run-001",
            "task_id": "task_a",
            "status": "SUCCESS",
            "data": {
                "result": 42
            },
        },
    )

    print("Broadcast completed.")

    print("Messages received:")

    print(websocket.messages)

    if len(websocket.messages) == 1:

        print(
            "WebSocket manager test PASSED!"
        )

    else:

        print(
            "WebSocket manager test FAILED!"
        )


if __name__ == "__main__":

    asyncio.run(main())