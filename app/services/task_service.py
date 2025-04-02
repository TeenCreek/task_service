import asyncio
import json
from datetime import datetime
from uuid import UUID

import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models.task import TaskStatus
from app.repositories.task import TaskRepository

QUEUE_NAME = 'tasks_queue'


async def publish_task(task_id: str, priority: int):
    try:
        connection = await aio_pika.connect_robust(
            settings.rabbitmq_url, timeout=10
        )
        async with connection:
            channel = await connection.channel()
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
            logger.info(f'Task {task_id} published with priority {priority}')
    except Exception as e:
        logger.error(f'Failed to publish task {task_id}: {str(e)}')
        raise


async def process_task(session: AsyncSession, task_id: str):
    repo = TaskRepository(session)
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        logger.error(f'Invalid task ID format: {task_id}')
        return

    try:
        async with session.begin():
            task = await repo.get(task_uuid)
            if not task or task.status != TaskStatus.PENDING:
                return

            await repo.update_status(
                task, TaskStatus.IN_PROGRESS, started_at=datetime.utcnow()
            )
            await session.flush()

            await asyncio.sleep(10 - task.priority.value * 2)

            await repo.update_status(
                task,
                TaskStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result='Task processed successfully',
            )
            logger.info(f'Task {task_id} completed successfully')

    except Exception as e:
        logger.error(f'Task {task_id} failed: {str(e)}')
        await repo.update_status(
            task,
            TaskStatus.FAILED,
            completed_at=datetime.utcnow(),
            error=str(e),
        )
