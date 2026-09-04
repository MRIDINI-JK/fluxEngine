from backend.event_bus import EventConsumer
from backend.event_bus.events import Event, EventType
from backend.monitoring.collector import MetricsCollector
import asyncio
from datetime import datetime, timezone

from backend.event_bus import EventType
class WorkerMonitor:

    def __init__(self, rabbitmq):
        self.monitor_task = None

        self.heartbeat_timeout = 30
        self.rabbitmq = rabbitmq

        self.workers = {}

        self.consumer = EventConsumer(
            rabbitmq
        )
        self.metrics = MetricsCollector()
    async def start(self):

        await self.consumer.subscribe(
            queue_name="flux.worker.monitor",

            routing_keys=[
                EventType.WORKER_REGISTERED.value,
                EventType.WORKER_HEARTBEAT.value,
                EventType.WORKER_OFFLINE.value,
            ],

            handler=self.handle_event,
        )

        print(
            "Worker monitoring started."
        )
        self.monitor_task = asyncio.create_task(
            self._check_workers()
    )

    async def handle_event(
        self,
        event: Event,
    ):

        worker_id = event.payload.get(
        "worker_id"
    )

        if worker_id is None:
            return

        if (
            event.event_type
            == EventType.WORKER_REGISTERED
        ):

            self.workers[worker_id] = {
                "worker_id": worker_id,

                "hostname":
                    event.payload.get(
                        "hostname",
                        "unknown",
                    ),

                "capabilities":
                    event.payload.get(
                        "capabilities",
                        [],
                    ),

                "busy": False,

                "last_heartbeat":
                    event.payload.get(
                        "timestamp"
                    ),
            }
            self.metrics.workers_registered(
                len(self.workers)
)
            print(
                f"Worker registered: "
                f"{worker_id}"
            )

        elif (
            event.event_type
            == EventType.WORKER_HEARTBEAT
        ):

            worker = self.workers.get(
                worker_id
            )

            if worker is None:

                self.workers[worker_id] = {
                "worker_id": worker_id,
                "hostname": event.payload.get("hostname", "unknown"),
                "capabilities": event.payload.get("capabilities", []),
                "busy": event.payload.get("busy", False),
                "last_heartbeat": event.payload.get("timestamp"),
        }

                self.metrics.workers_registered(len(self.workers))

                print(
                f"Worker discovered from heartbeat: {worker_id}"
        )

            else:
                worker["last_heartbeat"] = event.payload.get("timestamp")
                worker["busy"] = event.payload.get("busy", False)
                
            
        elif (
            event.event_type
            == EventType.WORKER_OFFLINE
        ):

            self.workers.pop(
                worker_id,
                None,
            )
            self.metrics.workers_registered(
                len(self.workers)
)
            print(
                f"Worker offline: "
                f"{worker_id}"
            )

    def get_workers(self):

        return list(
            self.workers.values()
        )
    async def _check_workers(self):

        while True:

            try:

                now = datetime.now(
                    timezone.utc
                )

                offline_workers = []

                for worker_id, worker in list(
                    self.workers.items()
            ):

                    heartbeat = worker.get(
                        "last_heartbeat"
                )

                    if heartbeat is None:
                        continue

                    heartbeat_time = datetime.fromisoformat(
                        heartbeat
                )

                    elapsed = (
                        now - heartbeat_time
                    ).total_seconds()

                    if (
                        elapsed
                        > self.heartbeat_timeout
                    ):

                        offline_workers.append(
                            worker_id
                    )

                for worker_id in offline_workers:

                    self.workers.pop(
                        worker_id,
                        None,
                )

                    print(
                        f"Worker offline: "
                        f"{worker_id}"
                )

                await asyncio.sleep(10)

            except asyncio.CancelledError:

                break

            except Exception as exc:

                print(
                    f"Worker monitor error: "
                    f"{exc}"
            )

                await asyncio.sleep(10)