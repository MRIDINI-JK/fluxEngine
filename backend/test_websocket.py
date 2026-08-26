import asyncio
import json

import websockets


async def main():

    workflow_run_id = "test-run-001"

    url = (
        "ws://127.0.0.1:8000"
        f"/ws/workflows/{workflow_run_id}"
    )

    async with websockets.connect(
        url
    ) as websocket:

        print(
            "Connected to FluxEngine WebSocket"
        )

        while True:

            message = await websocket.recv()

            print(
                "Received:"
            )

            print(
                json.loads(message)
            )


if __name__ == "__main__":

    asyncio.run(main())