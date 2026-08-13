from sqlalchemy import Column, ForeignKey, Integer, String

from backend.database import Base


class TaskRun(Base):
    __tablename__ = "task_runs"

    id = Column(Integer, primary_key=True)

    workflow_run_id = Column(
        Integer,
        ForeignKey("workflow_runs.id")
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id")
    )

    status = Column(String(30))

    retries = Column(Integer, default=0)