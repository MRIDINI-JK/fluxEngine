from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class WorkerInfo:

    worker_id: str

    hostname: str

    capabilities: set[str] = field(
        default_factory=set
    )

    last_heartbeat: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    busy: bool = False


class WorkerRegistry:

    def __init__(self):

        self.workers: dict[
            str,
            WorkerInfo
        ] = {}

    def register(
        self,
        worker: WorkerInfo,
    ):

        self.workers[
            worker.worker_id
        ] = worker

    def heartbeat(
        self,
        worker_id: str,
    ):

        worker = self.workers.get(
            worker_id
        )

        if worker:

            worker.last_heartbeat = (
                datetime.now(timezone.utc)
            )

    def unregister(
        self,
        worker_id: str,
    ):

        self.workers.pop(
            worker_id,
            None,
        )

    def get_workers(
        self,
    ) -> list[WorkerInfo]:

        return list(
            self.workers.values()
        )

    def find_worker(
        self,
        task_type: str,
    ) -> WorkerInfo | None:

        for worker in self.workers.values():

            if (
                task_type
                in worker.capabilities
                and not worker.busy
            ):

                return worker

        return None