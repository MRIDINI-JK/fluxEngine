from backend.scheduler.job import ScheduledJob


class SchedulerStore:

    def __init__(self):

        self.jobs: dict[
            str,
            ScheduledJob
        ] = {}

    async def save(
        self,
        job: ScheduledJob,
    ):

        self.jobs[
            job.job_id
        ] = job

    async def get(
        self,
        job_id: str,
    ) -> ScheduledJob | None:

        return self.jobs.get(
            job_id
        )

    async def delete(
        self,
        job_id: str,
    ):

        self.jobs.pop(
            job_id,
            None,
        )

    async def get_all(
        self,
    ) -> list[ScheduledJob]:

        return list(
            self.jobs.values()
        )