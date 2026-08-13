from backend.workflow_engine.graph import WorkflowGraph
from backend.workflow_engine.parser import (
    WorkflowDefinition,
    parse_workflow,
)
from backend.workflow_engine.validator import (
    WorkflowValidator,
)


class CompiledWorkflow:

    def __init__(
        self,
        definition: WorkflowDefinition,
        graph: WorkflowGraph,
    ):

        self.definition = definition
        self.graph = graph


class WorkflowCompiler:

    def __init__(self):

        self.validator = WorkflowValidator()

    def compile(
        self,
        data: dict,
    ) -> CompiledWorkflow:

        definition = parse_workflow(data)

        graph = WorkflowGraph()

        # Build nodes
        for node in definition.nodes:

            graph.add_node(
                node_id=node.id,
                node_type=node.type,
                config=node.config,
            )

        # Build edges
        for edge in definition.edges:

            graph.add_edge(
                source=edge.source,
                target=edge.target,
            )

        # Validate
        self.validator.validate(graph)

        return CompiledWorkflow(
            definition=definition,
            graph=graph,
        )