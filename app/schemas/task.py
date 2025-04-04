from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.shared import TaskPriority, TaskStatus


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
    started_at: datetime | None
    completed_at: datetime | None
    result: str | None
    error: str | None

    model_config = {'from_attributes': True}


class TaskStatusOut(BaseModel):
    id: UUID
    status: TaskStatus

    model_config = {'from_attributes': True}
