import asyncio
import uuid

from backend.event_bus import RabbitMQ
from backend.event_bus.events import TaskMessage
from backend.monitoring import WorkerMonitor
from backend.dispatcher.dispatcher import TaskDispatcher


async def main():

    print("Starting task dispatcher test...")

    # ==========================================
    # 1. Connect RabbitMQ
    # ==========================================

    rabbitmq = RabbitMQ()
    await rabbitmq.connect()

    print("RabbitMQ connected")


    # ==========================================
    # 2. Start WorkerMonitor
    # ==========================================

    worker_monitor = WorkerMonitor(rabbitmq)

    await worker_monitor.start()

    print("WorkerMonitor started")


    # ==========================================
    # 3. Give monitor time to receive worker
    # ==========================================

    print("Waiting for worker registration...")

    for _ in range(10):

        workers = worker_monitor.get_workers()

        if workers:
            break

        await asyncio.sleep(1)


    print(f"Workers discovered: {len(worker_monitor.get_workers())}")

    for worker in worker_monitor.get_workers():
        print(worker)


    # ==========================================
    # 4. Create TaskDispatcher
    # ==========================================

    dispatcher = TaskDispatcher(
        rabbitmq=rabbitmq,
        worker_monitor=worker_monitor,
    )


    # ==========================================
    # 5. Create Task
    # ==========================================

    task = TaskMessage(
        task_run_id=str(uuid.uuid4()),
        workflow_run_id="workflow-001",
        task_id="task_a",
        task_type="python",
        payload={
            "value": 21
        },
    )


    # ==========================================
    # 6. Dispatch task
    # ==========================================

    print("Dispatching task...")

    worker = await dispatcher.dispatch(task)

    if worker is None:

        print("ERROR: No available worker found.")

    else:

        print(
            f"Task dispatched to worker: "
            f"{worker['worker_id']}"
        )


    # ==========================================
    # 7. Keep connection alive briefly
    # ==========================================

    await asyncio.sleep(5)


    # ==========================================
    # 8. Cleanup
    # ==========================================

    await worker_monitor.consumer.stop()

    await rabbitmq.close()

    print("Task dispatcher test completed.")


if __name__ == "__main__":
    asyncio.run(main())