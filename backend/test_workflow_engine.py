from backend.workflow_engine import WorkflowCompiler


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


print("Starting workflow engine test...")

compiler = WorkflowCompiler()

compiled = compiler.compile(workflow)

print("Workflow compiled successfully!")

print(f"Name: {compiled.definition.name}")

print(f"Version: {compiled.definition.version}")

print(f"Nodes: {len(compiled.graph.nodes)}")

print("\nGraph:")

for node in compiled.graph.nodes.values():

    print(
        f"{node.id}: "
        f"dependencies={node.dependencies}, "
        f"dependents={node.dependents}"
    )