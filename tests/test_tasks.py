import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.session import get_db_session
from app.main import app

TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def _get_test_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = _get_test_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_task(client):
    payload = {
        'name': 'Test Task',
        'description': 'Test desc',
        'priority': 'LOW',
    }
    response = await client.post('/api/v1/tasks', json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == payload['name']
    assert data['description'] == payload['description']
    assert data['priority'] == payload['priority']


@pytest.mark.asyncio
async def test_get_tasks(client):
    payload = {
        'name': 'Sample Task',
        'description': 'Some description',
        'priority': 'HIGH',
    }
    await client.post('/api/v1/tasks', json=payload)

    response = await client.get('/api/v1/tasks')
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert 'items' in data
    assert isinstance(data['items'], list)

    assert any(task['name'] == 'Sample Task' for task in data['items'])


@pytest.mark.asyncio
async def test_get_task_with_invalid_id(client):
    invalid_id = '00000000-0000-0000-0000-000000000000'
    response = await client.get(f'/api/v1/tasks/{invalid_id}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Task not found'}
