from sqlalchemy import JSON, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.database import Base


class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"

    id = Column(Integer, primary_key=True)

    workflow_id = Column(Integer,
                         ForeignKey("workflows.id"))

    version = Column(Integer)

    definition = Column(JSON)

    workflow = relationship("Workflow")