import asyncio

from backend.workflow_engine import (
    WorkflowCompiler,
    WorkflowExecutor,
)


workflow = {
    "name": "Execution Test",
    "version": 1,

    "nodes": [
        {
            "id": "start",
            "type": "start",
        },
        {
            "id": "task_a",
            "type": "python",
            "config": {
                "value": 10,
            },
        },
        {
            "id": "task_b",
            "type": "python",
            "config": {
                "value": 20,
            },
        },
        {
            "id": "end",
            "type": "end",
        },
    ],

    "edges": [
        {
            "source": "start",
            "target": "task_a",
        },
        {
            "source": "task_a",
            "target": "task_b",
        },
        {
            "source": "task_b",
            "target": "end",
        },
    ],
}


async def python_handler(context):

    value = context["config"]["value"]

    print(
        f"Executing {context['task_id']} "
        f"with value {value}"
    )

    return value * 2


attempts = 0


async def failing_handler(context):

    global attempts

    attempts += 1

    print(
        f"Attempt {attempts}"
    )

    if attempts < 3:
        raise RuntimeError(
            "Temporary failure"
        )

    return "Success after retry"
async def main():

    compiler = WorkflowCompiler()

    compiled = compiler.compile(
        workflow
    )

    executor = WorkflowExecutor()

    executor.register_handler(
        "python",
        failing_handler,
    )

    context = await executor.execute(
        workflow=compiled,
        workflow_run_id="run-001",
        input_data={
            "message": "Hello FluxEngine"
        },
    )

    print()
    print("Workflow completed!")
    print(f"Status: {context.status}")

    print(
        f"Outputs: {context.outputs}"
    )

    for task_id, task in context.tasks.items():

        print(
            f"{task_id}: "
            f"status={task.status}, "
            f"attempts={task.attempts}, "
            f"result={task.result}"
        )


if __name__ == "__main__":
    asyncio.run(main())