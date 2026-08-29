from fastapi import APIRouter
from fastapi.responses import Response

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from backend.monitoring import (
    check_system,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)


@router.get("/health")
async def health():

    return await check_system()


@router.get("/metrics")
async def metrics():

    data = generate_latest()

    return Response(
        content=data,
        media_type=CONTENT_TYPE_LATEST,
    )