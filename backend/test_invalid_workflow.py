from backend.workflow_engine import (
    WorkflowCompiler,
    WorkflowValidationError,
)


workflow = {
    "name": "Invalid Workflow",
    "version": 1,

    "nodes": [
        {
            "id": "start",
            "type": "start",
        },
        {
            "id": "task_a",
            "type": "python",
        },
        {
            "id": "task_b",
            "type": "python",
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
            "target": "task_a",
        },
        {
            "source": "task_b",
            "target": "end",
        },
    ],
}


compiler = WorkflowCompiler()

try:

    compiler.compile(workflow)

    print("ERROR: Invalid workflow was accepted.")

except WorkflowValidationError as exc:

    print("Validation correctly failed!")
    print(f"Reason: {exc}")