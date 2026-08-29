from backend.event_bus import EventConsumer
from backend.event_bus.events import EventType

from backend.monitoring.metrics import (
    TASKS_STARTED,
    TASKS_COMPLETED,
    TASKS_FAILED,
    TASKS_RETRIED,
    TASK_DURATION,
)


class TaskMonitor:

    def __init__(self, rabbitmq):

        self.rabbitmq = rabbitmq

        self.consumer = EventConsumer(
            rabbitmq
        )

    async def start(self):

        await self.consumer.subscribe(
            queue_name="flux.task.monitor",

            routing_keys=[
                EventType.TASK_STARTED.value,
                EventType.TASK_COMPLETED.value,
                EventType.TASK_FAILED.value,
            ],

            handler=self.handle_event,
        )

        print(
            "Task monitoring started."
        )

    async def handle_event(
        self,
        event,
    ):
        try: 
            print(
            f"Task event received: "
            f"{event.event_type}"
        )

            if (
                event.event_type
            == EventType.TASK_STARTED
        ):

                TASKS_STARTED.inc()

                print(
                f"Task started: "
                f"{event.payload.get('task_id')}"
            )

            elif (
                event.event_type
            == EventType.TASK_COMPLETED
        ):

                TASKS_COMPLETED.inc()
                print(
    "COMPLETED METRIC VALUE:",
    TASKS_COMPLETED._value.get()
)
                self._record_duration(
                
                event
            )

                self._record_retries(
                event
            )

                print(
                f"Task completed: "
                f"{event.payload.get('task_id')}"
            )

            elif (
                event.event_type
            == EventType.TASK_FAILED
        ):

                TASKS_FAILED.inc()

                self._record_duration(
                event
            )

                self._record_retries(
                event
            )

                print(
                f"Task failed: "
                f"{event.payload.get('task_id')}"
            )
        except Exception as e:
            print(
            "TASK MONITOR ERROR:",
            repr(exc)
        )

            raise

    def _record_duration(
        self,
        event,
    ):
        

        duration = event.payload.get(
            "duration"
        )
        print(
                "Duration payload: ",
                event.payload,
            )
        if duration is None:
            print( "No duration provided in event payload.")
            return

            
        duration = float(duration)

        print(
                "Duration value:",
                duration,
            )
        TASK_DURATION.observe(
                  duration
            )
#         print(
#     "DURATION COUNT:",
#     TASK_DURATION._count.get()

# )
        try:
            print("BEFORE HISTOGRAM OBSERVE")

            TASK_DURATION.observe(
                    duration
        )

            print("AFTER HISTOGRAM OBSERVE")
        except Exception as e:
            print(
                "HISTOGRAM ERROR:",
                repr(exc)
            )
            import traceback
            traceback.print_exc()

            raise
        
    def _record_retries(
        self,
        event,
    ):

        attempts = event.payload.get(
            "attempts",
            1,
        )

        if attempts > 1:

            TASKS_RETRIED.inc(
                attempts - 1
            )