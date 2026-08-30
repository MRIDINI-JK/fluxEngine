import asyncio

from backend.workflow_engine import (
    WorkflowCompiler,
    WorkflowExecutor,
)
from backend.monitoring.metrics import (
    WORKFLOWS_STARTED,
    WORKFLOWS_COMPLETED,
    WORKFLOWS_FAILED,
    WORKFLOWS_RUNNING,
    WORKFLOW_DURATION,
)


workflow = {
    "name": "Demo Workflow",
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
                "function": "process_a"
            },
        },
        {
            "id": "task_b",
            "type": "python",
            "config": {
                "function": "process_b"
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


async def process_a(data):

    print("Running process_a")

    return {
        "message": "Task A completed"
    }


async def process_b(data):

    print("Running process_b")

    return {
        "message": "Task B completed"
    }


async def main():

    print(
        "Starting workflow engine test..."
    )

    # ----------------------------------------
    # Compile
    # ----------------------------------------

    compiler = WorkflowCompiler()

    compiled = compiler.compile(
        workflow
    )

    print(
        "Workflow compiled successfully!"
    )

    print(
        f"Name: {compiled.definition.name}"
    )

    print(
        f"Version: "
        f"{compiled.definition.version}"
    )

    print(
        f"Nodes: "
        f"{len(compiled.graph.nodes)}"
    )

    print("\nGraph:")

    for node in compiled.graph.nodes.values():

        print(
            f"{node.id}: "
            f"dependencies={node.dependencies}, "
            f"dependents={node.dependents}"
        )

    # ----------------------------------------
    # Create executor
    # ----------------------------------------

    executor = WorkflowExecutor()

    # ----------------------------------------
    # Register handlers
    # ----------------------------------------

    executor.register_handler(
        "python",
        process_a,
    )

    # ----------------------------------------
    # Execute workflow
    # ----------------------------------------

    print(
        "\nExecuting workflow..."
    )

    context = await executor.execute(
        workflow=compiled,

        workflow_run_id="test-workflow-001",

        input_data={
            "value": 21
        },
    )
    print("\nWorkflow Metrics:")

    print(
    "Started:",
    WORKFLOWS_STARTED._value.get()
)

    print(
    "Completed:",
    WORKFLOWS_COMPLETED._value.get()
)

    print(
    "Failed:",
    WORKFLOWS_FAILED._value.get()
)

    print(
    "Running:",
    WORKFLOWS_RUNNING._value.get()
)
    # ----------------------------------------
    # Result
    # ----------------------------------------

    print(
        "\nWorkflow execution finished!"
    )

    print(
        f"Status: {context.status}"
    )

    print(
        f"Workflow Run ID: "
        f"{context.workflow_run_id}"
    )

    print(
        f"Outputs: "
        f"{context.outputs}"
    )


if __name__ == "__main__":

    asyncio.run(main())