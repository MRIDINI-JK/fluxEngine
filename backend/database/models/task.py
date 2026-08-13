from sqlalchemy import JSON, Column, Integer, String

from backend.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)

    name = Column(String(100))

    task_type = Column(String(50))

    configuration = Column(JSON)