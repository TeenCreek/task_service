import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
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
        return {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}[self.value]


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(
        SqlEnum(TaskPriority), default=TaskPriority.MEDIUM
    )
    status: Mapped[TaskStatus] = mapped_column(
        SqlEnum(TaskStatus), default=TaskStatus.NEW
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_priority', 'priority'),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, status={self.status}, priority={self.priority})>"

    def __str__(self):
        return f"Task '{self.name}' with status {self.status} and priority {self.priority}"
