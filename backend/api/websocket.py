from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from backend.websocket import (
    ConnectionManager,
)


router = APIRouter(
    tags=["WebSocket"]
)


manager = ConnectionManager()


@router.websocket(
    "/ws/workflows/{workflow_run_id}"
)
async def workflow_websocket(
    websocket: WebSocket,
    workflow_run_id: str,
):

    await manager.connect(
        workflow_run_id,
        websocket,
    )

    try:

        while True:

            # Keep the connection alive.
            # Client messages can be handled later.
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            workflow_run_id,
            websocket,
        )

    except Exception:

        manager.disconnect(
            workflow_run_id,
            websocket,
        )