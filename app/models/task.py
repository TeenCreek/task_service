import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Enum as SqlEnum

from app.db.database import Base


class TaskStatus(str, PyEnum):
    NEW = 'NEW'
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class TaskPriority(str, PyEnum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

    @property
    def numeric(self) -> int:
        mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        return mapping[self.value]


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(SqlEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(SqlEnum(TaskStatus), default=TaskStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result = Column(Text)
    error = Column(Text)
