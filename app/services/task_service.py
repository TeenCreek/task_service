import asyncio
import json
from datetime import datetime, timezone
from uuid import UUID

import aio_pika
from aio_pika.pool import Pool
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models.task import TaskPriority, TaskStatus
from app.repositories.task import TaskRepository

QUEUE_NAME = 'tasks_queue'


async def get_connection():
    return await aio_pika.connect_robust(settings.rabbitmq_url)


connection_pool = Pool(get_connection, max_size=10)


async def publish_task(task_id: str, priority: int):
    try:
        async with connection_pool.acquire() as connection:
            async with connection.channel() as channel:
                await channel.declare_queue(
                    QUEUE_NAME, durable=True, arguments={'x-max-priority': 10}
                )
                message = aio_pika.Message(
                    body=json.dumps({'task_id': task_id}).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    priority=priority,
                )
                await channel.default_exchange.publish(
                    message, routing_key=QUEUE_NAME
                )
    except Exception as e:
        logger.error(f'Failed to publish task {task_id}: {str(e)}')
        raise


async def process_task(session: AsyncSession, task_id: str):
    repo = TaskRepository(session)
    try:
        task_uuid = UUID(task_id)
        task = await repo.get(task_uuid)

        if not task or task.status != TaskStatus.PENDING:
            return

        priority = TaskPriority(task.priority).numeric
        await repo.update_status(
            task, TaskStatus.IN_PROGRESS, started_at=datetime.now(timezone.utc)
        )
        await asyncio.sleep(10 - priority * 2)

        await repo.update_status(
            task,
            TaskStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc),
            result='Success',
        )
    except Exception as e:
        logger.error(f'Task {task_id} failed: {str(e)}')
        if task:
            await repo.update_status(task, TaskStatus.FAILED, error=str(e))
    finally:
        await session.commit()
