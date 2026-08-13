
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.database import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True)

    workflow_id = Column(
        Integer,
        ForeignKey("workflows.id")
    )

    version = Column(Integer)

    status = Column(String(30))

    started_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    completed_at = Column(DateTime(timezone=True))