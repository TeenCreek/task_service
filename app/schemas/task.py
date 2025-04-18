from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    error: str | None = None

    model_config = {'from_attributes': True}


class TaskStatusOut(BaseModel):
    status: TaskStatus
    id: UUID

    model_config = {'from_attributes': True}
