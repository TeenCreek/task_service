from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.task import TaskStatus  # Import TaskStatus from the model
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskOut, TaskStatusOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut)
async def create_task(
    task_in: TaskCreate, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    task = Task(**task_in.model_dump())
    task = await repo.create(task)
    return task


@router.get("", response_model=Page[TaskOut])
async def list_tasks(
    session: AsyncSession = Depends(get_db_session),
    status: TaskStatusOut | None = None,  # Use TaskStatusOut for the input
):
    repo = TaskRepository(session)
    # Convert TaskStatusOut to TaskStatus if status is provided
    task_status = TaskStatus(status) if status else None
    tasks = await repo.list(status=task_status)
    return paginate(tasks)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: UUID, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    if task := await repo.get(task_id):
        return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
    )


@router.delete("/{task_id}", response_model=TaskOut)
async def cancel_task(
    task_id: UUID, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    task = await repo.get(task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")

    if task.status not in (TaskStatus.NEW, TaskStatus.PENDING):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Cannot cancel task in current status"
        )

    task = await repo.update_status(task, TaskStatus.CANCELLED)
    return task
