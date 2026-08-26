import uuid
from datetime import datetime

from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.api.schemas import (
    ScheduleCreate,
    ScheduleResponse,
)

from backend.scheduler import (
    FluxScheduler,
    ScheduledJob,
)

from backend.scheduler.cron import (
    CronParser,
)


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


scheduler = FluxScheduler()


@router.post(
    "",
    response_model=ScheduleResponse,
)
async def create_schedule(
    request: ScheduleCreate,
):

    if (
        not request.cron_expression
        and not request.run_at
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Either cron_expression "
                "or run_at is required"
            ),
        )

    if request.cron_expression:

        if not CronParser.validate(
            request.cron_expression
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid cron expression",
            )

    job_id = str(
        uuid.uuid4()
    )

    run_at = None

    if request.run_at:

        try:

            run_at = datetime.fromisoformat(
                request.run_at
            )

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail="Invalid run_at datetime",
            )

    job = ScheduledJob(
        job_id=job_id,

        workflow_id=request.workflow_id,

        name=request.name,

        cron_expression=(
            request.cron_expression
        ),

        run_at=run_at,

        enabled=request.enabled,

        input_data=request.input_data,
    )

    if request.cron_expression:

        await scheduler.add_cron_job(
            job
        )

    else:

        await scheduler.add_one_time_job(
            job
        )

    return {
        "job_id": job_id,
        "workflow_id": request.workflow_id,
        "name": request.name,
        "cron_expression": (
            request.cron_expression
        ),
        "run_at": (
            run_at.isoformat()
            if run_at
            else None
        ),
        "enabled": request.enabled,
    }