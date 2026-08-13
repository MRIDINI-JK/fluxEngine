from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from backend.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    event_type = Column(String(100))

    payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())