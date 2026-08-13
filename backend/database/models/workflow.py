from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from backend.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=False)

    description = Column(Text)

    created_by = Column(String(100))

    current_version = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        onupdate=func.now())