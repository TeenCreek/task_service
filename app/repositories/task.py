from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
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
        self, task: Task, status: TaskStatus, **kwargs
    ) -> Task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        task.status = status
        await self.session.commit()
        await self.session.refresh(task)
        return task
