
from backend.workflow_engine.graph import WorkflowGraph


class WorkflowValidationError(Exception):
    pass


class WorkflowValidator:

    def validate(self, graph: WorkflowGraph):

        self._validate_empty(graph)

        self._validate_start_node(graph)

        self._validate_end_node(graph)

        self._validate_dependencies(graph)

        self._validate_cycles(graph)

        return True

    def _validate_empty(
        self,
        graph: WorkflowGraph,
    ):

        if not graph.nodes:
            raise WorkflowValidationError(
                "Workflow contains no nodes"
            )

    def _validate_start_node(
        self,
        graph: WorkflowGraph,
    ):

        start_nodes = [
            node
            for node in graph.nodes.values()
            if node.node_type == "start"
        ]

        if len(start_nodes) != 1:

            raise WorkflowValidationError(
                f"Workflow must contain exactly "
                f"one start node. Found {len(start_nodes)}."
            )

    def _validate_end_node(
        self,
        graph: WorkflowGraph,
    ):

        end_nodes = [
            node
            for node in graph.nodes.values()
            if node.node_type == "end"
        ]

        if len(end_nodes) != 1:

            raise WorkflowValidationError(
                f"Workflow must contain exactly "
                f"one end node. Found {len(end_nodes)}."
            )

    def _validate_dependencies(
        self,
        graph: WorkflowGraph,
    ):

        start_nodes = [
            node
            for node in graph.nodes.values()
            if node.node_type == "start"
        ]

        end_nodes = [
            node
            for node in graph.nodes.values()
            if node.node_type == "end"
        ]

        start = start_nodes[0]
        end = end_nodes[0]

        if start.dependencies:
            raise WorkflowValidationError(
                "Start node cannot have dependencies"
            )

        if end.dependents:
            raise WorkflowValidationError(
                "End node cannot have outgoing edges"
            )

    def _validate_cycles(
        self,
        graph: WorkflowGraph,
    ):

        visited = set()
        visiting = set()

        def visit(node_id: str):

            if node_id in visiting:

                raise WorkflowValidationError(
                    f"Cycle detected involving node: {node_id}"
                )

            if node_id in visited:
                return

            visiting.add(node_id)

            node = graph.get_node(node_id)

            for dependent in node.dependents:
                visit(dependent)

            visiting.remove(node_id)

            visited.add(node_id)

        for node_id in graph.nodes:

            visit(node_id)