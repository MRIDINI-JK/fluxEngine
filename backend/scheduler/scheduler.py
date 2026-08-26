import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)
from apscheduler.triggers.cron import (
    CronTrigger,
)
from apscheduler.triggers.date import (
    DateTrigger,
)

from backend.common.logger import logger

from backend.event_bus import (
    Event,
    EventType,
    EventProducer,
    RabbitMQ,
)

from backend.scheduler.job import (
    ScheduledJob,
)

from backend.scheduler.registry import (
    SchedulerRegistry,
)

from backend.scheduler.store import (
    SchedulerStore,
)


class FluxScheduler:

    def __init__(self):

        self.scheduler = (
            AsyncIOScheduler()
        )

        self.rabbitmq = RabbitMQ()

        self.producer: EventProducer | None = None

        self.registry = (
            SchedulerRegistry()
        )

        self.store = (
            SchedulerStore()
        )

    async def start(self):

        await self.rabbitmq.connect()

        self.producer = EventProducer(
            self.rabbitmq
        )

        self.scheduler.start()

        logger.info(
            "FluxEngine scheduler started"
        )

    async def shutdown(self):

        self.scheduler.shutdown()

        await self.rabbitmq.close()

        logger.info(
            "FluxEngine scheduler stopped"
        )

    async def add_cron_job(
        self,
        job: ScheduledJob,
    ):

        if not job.cron_expression:

            raise ValueError(
                "Cron expression required"
            )

        await self.store.save(
            job
        )

        self.registry.add(
            job
        )

        trigger = CronTrigger.from_crontab(
            job.cron_expression
        )

        self.scheduler.add_job(
            self._trigger_workflow,
            trigger=trigger,
            id=job.job_id,
            args=[job],
            replace_existing=True,
        )

        logger.info(
            f"Scheduled cron job: "
            f"{job.job_id}"
        )

    async def add_one_time_job(
        self,
        job: ScheduledJob,
    ):

        if not job.run_at:

            raise ValueError(
                "run_at is required"
            )

        await self.store.save(
            job
        )

        self.registry.add(
            job
        )

        trigger = DateTrigger(
            run_date=job.run_at
        )

        self.scheduler.add_job(
            self._trigger_workflow,
            trigger=trigger,
            id=job.job_id,
            args=[job],
            replace_existing=True,
        )

        logger.info(
            f"Scheduled one-time job: "
            f"{job.job_id}"
        )

    async def remove_job(
        self,
        job_id: str,
    ):

        try:

            self.scheduler.remove_job(
                job_id
            )

        except Exception:
            pass

        self.registry.remove(
            job_id
        )

        await self.store.delete(
            job_id
        )

    async def _trigger_workflow(
        self,
        job: ScheduledJob,
    ):

        if not job.enabled:

            logger.info(
                f"Job disabled: "
                f"{job.job_id}"
            )

            return

        if self.producer is None:

            raise RuntimeError(
                "Scheduler is not connected "
                "to RabbitMQ"
            )

        workflow_run_id = str(
            uuid.uuid4()
        )

        event = Event(
            event_id=str(
                uuid.uuid4()
            ),

            event_type=(
                EventType.WORKFLOW_STARTED
            ),

            source="scheduler",

            workflow_id=job.workflow_id,

            workflow_run_id=(
                workflow_run_id
            ),

            payload={
                "job_id": job.job_id,

                "input": job.input_data,

                "scheduled_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            },
        )

        await self.producer.publish(
            event
        )

        logger.info(
            f"Triggered workflow "
            f"{job.workflow_id} "
            f"run={workflow_run_id}"
        )