import pytest

from app.models.task import TaskStatus
from app.services.task_service import process_task


@pytest.mark.asyncio
async def test_process_task(async_session, mock_task):
    from datetime import datetime, timezone

    await async_session.add(mock_task)
    await async_session.commit()

    await process_task(async_session, str(mock_task.id))

    async_session.refresh(mock_task)
    assert mock_task.status == TaskStatus.COMPLETED
    assert mock_task.completed_at is not None
