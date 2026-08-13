from sqlalchemy import Boolean, Column, Integer, String

from backend.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)

    workflow_id = Column(Integer)

    cron_expression = Column(String(100))

    enabled = Column(Boolean, default=True)