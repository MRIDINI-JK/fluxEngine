from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):

        self.connections: dict[
            str,
            set[WebSocket]
        ] = defaultdict(set)

    async def connect(
        self,
        workflow_run_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        self.connections[
            workflow_run_id
        ].add(websocket)

    def disconnect(
        self,
        workflow_run_id: str,
        websocket: WebSocket,
    ):

        connections = self.connections.get(
            workflow_run_id
        )

        if not connections:
            return

        connections.discard(
            websocket
        )

        if not connections:

            self.connections.pop(
                workflow_run_id,
                None,
            )

    async def broadcast(
        self,
        workflow_run_id: str,
        message: dict,
    ):

        connections = self.connections.get(
            workflow_run_id,
            set(),
        )

        disconnected = []

        for websocket in connections:

            try:

                await websocket.send_json(
                    message
                )

            except Exception:

                disconnected.append(
                    websocket
                )

        for websocket in disconnected:

            self.disconnect(
                workflow_run_id,
                websocket,
            )

    def connection_count(
        self,
        workflow_run_id: str,
    ) -> int:

        return len(
            self.connections.get(
                workflow_run_id,
                set(),
            )
        )