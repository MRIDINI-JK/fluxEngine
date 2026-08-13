from pydantic import BaseModel, Field


class NodeDefinition(BaseModel):
    id: str
    type: str
    config: dict = Field(default_factory=dict)


class EdgeDefinition(BaseModel):
    source: str
    target: str


class WorkflowDefinition(BaseModel):
    name: str
    version: int = 1

    nodes: list[NodeDefinition]
    edges: list[EdgeDefinition]


def parse_workflow(data: dict) -> WorkflowDefinition:
    """
    Convert raw workflow JSON into a validated
    WorkflowDefinition object.
    """

    return WorkflowDefinition.model_validate(data)