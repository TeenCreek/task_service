import uuid
from datetime import datetime
from enum import Enum as PyEnum  # Renamed to avoid conflict

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Enum as SqlEnum  # Renamed to avoid conflict

from app.db.database import Base


class TaskStatus(str, PyEnum):  # Use Python's Enum for defining enumerations
    NEW = "NEW"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskPriority(str, PyEnum):  # Use Python's Enum for defining enumerations
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(
        SqlEnum(TaskPriority), default=TaskPriority.MEDIUM
    )  # Use SqlAlchemy Enum for DB columns
    status = Column(
        SqlEnum(TaskStatus), default=TaskStatus.NEW
    )  # Use SqlAlchemy Enum for DB columns
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result = Column(Text)
    error = Column(Text)
