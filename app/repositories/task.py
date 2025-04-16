from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def model_from_schema(self, task_create: TaskCreate) -> Task:
        return Task(
            name=task_create.name,
            description=task_create.description,
            priority=task_create.priority,
        )

    async def create(self, task: Task) -> Task:
        self.session.add(task)

        try:
            await self.session.commit()
            await self.session.refresh(task)

        except Exception as e:
            raise ValueError(f'Error when creating a task: {str(e)}')

        return task

    async def get(self, task_id: UUID) -> Task | None:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )

        return result.scalars().first()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TaskStatus | None = None,
    ) -> Sequence[Task]:
        stmt = select(Task).offset(skip).limit(limit)
        if status:
            stmt = stmt.where(Task.status == status)
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def update_status(
        self, task: Task, new_status: TaskStatus, **kwargs
    ):
        valid_transitions = {
            TaskStatus.NEW: [TaskStatus.PENDING, TaskStatus.CANCELLED],
            TaskStatus.PENDING: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.CANCELLED,
                TaskStatus.FAILED,
            ],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.FAILED],
        }

        if new_status not in valid_transitions.get(task.status, []):
            raise ValueError(
                f'Invalid status transition from {task.status} to {new_status}'
            )

        for key, value in kwargs.items():
            setattr(task, key, value)

        task.status = new_status

        await self.session.flush()
        await self.session.refresh(task)

        return task
