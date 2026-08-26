from backend.scheduler.job import ScheduledJob


class SchedulerRegistry:

    def __init__(self):

        self.jobs: dict[
            str,
            ScheduledJob
        ] = {}

    def add(
        self,
        job: ScheduledJob,
    ):

        if job.job_id in self.jobs:

            raise ValueError(
                f"Job already exists: "
                f"{job.job_id}"
            )

        self.jobs[
            job.job_id
        ] = job

    def get(
        self,
        job_id: str,
    ) -> ScheduledJob | None:

        return self.jobs.get(
            job_id
        )

    def remove(
        self,
        job_id: str,
    ):

        self.jobs.pop(
            job_id,
            None,
        )

    def all(
        self,
    ) -> list[ScheduledJob]:

        return list(
            self.jobs.values()
        )