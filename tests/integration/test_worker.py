import asyncio

import pytest

from app.models.task import TaskStatus
from app.services.task_service import publish_task


@pytest.mark.asyncio
async def test_worker_processes_task(api_client, async_session, created_task):
    await publish_task(created_task['id'], priority=5)

    await asyncio.sleep(3)

    response = await api_client.get(f'/api/v1/tasks/{created_task['id']}')
    task = response.json()

    assert task['status'] == TaskStatus.COMPLETED
    assert task['completed_at'] is not None
