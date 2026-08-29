from fastapi import APIRouter, Request


router = APIRouter(
    prefix="/workers",
    tags=["Workers"],
)


@router.get("")
async def list_workers(
    request: Request,
):

    worker_monitor = getattr(
        request.app.state,
        "worker_monitor",
        None,
    )

    if worker_monitor is None:
        return []

    return worker_monitor.get_workers()