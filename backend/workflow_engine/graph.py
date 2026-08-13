from dataclasses import dataclass, field


@dataclass
class GraphNode:
    id: str
    node_type: str
    config: dict = field(default_factory=dict)

    dependencies: set[str] = field(default_factory=set)

    dependents: set[str] = field(default_factory=set)


class WorkflowGraph:

    def __init__(self):

        self.nodes: dict[str, GraphNode] = {}

    def add_node(
        self,
        node_id: str,
        node_type: str,
        config: dict | None = None,
    ):

        if node_id in self.nodes:
            raise ValueError(
                f"Duplicate node ID: {node_id}"
            )

        self.nodes[node_id] = GraphNode(
            id=node_id,
            node_type=node_type,
            config=config or {},
        )

    def add_edge(
        self,
        source: str,
        target: str,
    ):

        if source not in self.nodes:
            raise ValueError(
                f"Unknown source node: {source}"
            )

        if target not in self.nodes:
            raise ValueError(
                f"Unknown target node: {target}"
            )

        if source == target:
            raise ValueError(
                f"Self-loop detected: {source}"
            )

        self.nodes[target].dependencies.add(source)

        self.nodes[source].dependents.add(target)

    def get_node(self, node_id: str) -> GraphNode:

        if node_id not in self.nodes:
            raise KeyError(
                f"Node not found: {node_id}"
            )

        return self.nodes[node_id]