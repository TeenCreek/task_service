import pytest
from httpx import AsyncClient

from app.models.task import TaskStatus


@pytest.mark.asyncio
async def test_create_task(api_client: AsyncClient):
    response = await api_client.post(
        '/api/v1/tasks',
        json={
            'name': 'Test Task',
            'description': 'Task description',
            'priority': 'MEDIUM',
        },
    )

    assert response.status_code == 201
    task = response.json()
    assert task['name'] == 'Test Task'
    assert task['status'] == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_get_task(api_client: AsyncClient, created_task):
    response = await api_client.get(f'/api/v1/tasks/{created_task['id']}')

    assert response.status_code == 200
    task = response.json()
    assert task['id'] == created_task['id']
    assert task['status'] == TaskStatus.PENDING
