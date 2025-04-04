from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models.task import Task, TaskPriority, TaskStatus
from app.repositories.task import TaskRepository


@pytest.fixture
def mock_task():
    return Task(
        id=uuid4(),
        name='Test Task',
        description='Test Description',
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.NEW,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_task(async_session, mock_task):
    repo = TaskRepository(async_session)
    task = await repo.create(mock_task)

    assert task.id == mock_task.id
    assert task.status == TaskStatus.NEW


@pytest.mark.asyncio
async def test_update_task_status(async_session, mock_task):
    repo = TaskRepository(async_session)
    await repo.create(mock_task)

    updated_task = await repo.update_status(mock_task, TaskStatus.PENDING)

    assert updated_task.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_invalid_status_transition(async_session, mock_task):
    repo = TaskRepository(async_session)
    await repo.create(mock_task)

    with pytest.raises(ValueError):
        await repo.update_status(mock_task, TaskStatus.COMPLETED)
