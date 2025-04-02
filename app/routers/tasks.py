from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.task import TaskStatus
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskOut, TaskStatusOut
from app.services.task_service import publish_task

router = APIRouter(prefix='/api/v1/tasks', tags=['tasks'])


@router.post('', response_model=TaskOut, status_code=201)
async def create_task(
    task_in: TaskCreate, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    task = repo.model_from_schema(task_in)
    task = await repo.create(task)
    await publish_task(str(task.id), task.priority.numeric)
    return TaskOut.from_orm(task)


@router.get('', response_model=Page[TaskOut])
async def list_tasks(
    session: AsyncSession = Depends(get_db_session),
    status: TaskStatus | None = None,
):
    repo = TaskRepository(session)
    tasks = await repo.list(status=status)
    return paginate([TaskOut.from_orm(t) for t in tasks])


@router.get('/{task_id}', response_model=TaskOut)
async def get_task(
    task_id: UUID, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    if task := await repo.get(task_id):
        return TaskOut.from_orm(task)
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Task not found')


@router.delete('/{task_id}', response_model=TaskOut)
async def cancel_task(
    task_id: UUID, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    task = await repo.get(task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Task not found')

    if task.status not in (TaskStatus.NEW, TaskStatus.PENDING):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, 'Cannot cancel task in current status'
        )

    try:
        task = await repo.update_status(task, TaskStatus.CANCELLED)
        return TaskOut.from_orm(task)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))


@router.get('/{task_id}/status', response_model=TaskStatusOut)
async def get_task_status(
    task_id: UUID, session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    if task := await repo.get(task_id):
        return TaskStatusOut(id=task.id, status=task.status)
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Task not found')
