import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_full_workflow():
    response = client.post(
        '/api/v1/tasks',
        json={
            'name': 'Test Task',
            'description': 'Integration test task',
            'priority': 'HIGH',
        },
    )
    assert response.status_code == 201
    task_id = response.json()['id']

    status_response = client.get(f'/api/v1/tasks/{task_id}/status')
    assert status_response.status_code == 200
    assert status_response.json()['status'] in ['NEW', 'PENDING']

    cancel_response = client.delete(f'/api/v1/tasks/{task_id}')
    assert cancel_response.status_code == 200
    assert cancel_response.json()['status'] == 'CANCELLED'

    error_response = client.delete(f'/api/v1/tasks/{task_id}')
    assert error_response.status_code == 400


def test_invalid_task():
    fake_id = uuid.uuid4()
    response = client.get(f'/api/v1/tasks/{fake_id}')
    assert response.status_code == 404
