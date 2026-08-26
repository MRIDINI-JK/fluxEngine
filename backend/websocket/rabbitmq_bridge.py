from backend.event_bus import (
    Event,
    EventConsumer,
    RabbitMQ,
)

from backend.websocket import (
    WebSocketService,
)


class RabbitMQWebSocketBridge:

    def __init__(
        self,
        rabbitmq: RabbitMQ,
        websocket_service: WebSocketService,
    ):

        self.rabbitmq = rabbitmq

        self.websocket_service = (
            websocket_service
        )

        self.consumer = EventConsumer(
            rabbitmq
        )

    async def start(self):

        await self.consumer.subscribe(
            queue_name="flux.websocket",

            routing_keys=[
                "workflow.started",
                "workflow.completed",
                "workflow.failed",
                "workflow.cancelled",
                "task.started",
                "task.completed",
                "task.failed",
            ],

            handler=self.handle_event,
        )

    async def handle_event(
        self,
        event: Event,
    ):

        if event.workflow_run_id is None:

            return

        message = {
            "event_type":
                event.event_type.value,

            "workflow_run_id":
                str(event.workflow_run_id),

            "task_id":
                (
                    str(event.task_id)
                    if event.task_id
                    else None
                ),

            "data":
                event.payload,
        }

        await self.websocket_service.publish(
            str(event.workflow_run_id),
            message,
        )