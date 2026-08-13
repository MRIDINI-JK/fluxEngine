from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from backend.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)

    hostname = Column(String(100))

    status = Column(String(30))

    last_seen = Column(DateTime(timezone=True),
                       server_default=func.now())

    current_task = Column(Integer)