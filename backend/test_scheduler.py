import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from backend.scheduler import (
    FluxScheduler,
    ScheduledJob,
)


async def main():

    scheduler = FluxScheduler()

    await scheduler.start()

    job = ScheduledJob(
        job_id=str(uuid.uuid4()),

        workflow_id=1,

        name="One Time Test",

        run_at=(
            datetime.now(timezone.utc)
        +   timedelta(seconds=10)
        ),

    input_data={
        "message": "Delayed workflow"
    },
    )

    await scheduler.add_one_time_job(
        job
    )

    print(
        "Scheduler running..."
    )

    print(
        "Workflow will trigger every minute."
    )

    try:

        while True:

            await asyncio.sleep(10)

    except KeyboardInterrupt:

        await scheduler.shutdown()


if __name__ == "__main__":

    asyncio.run(main())