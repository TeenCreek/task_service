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


async def publish_task(task_id: str, priority: int, session: AsyncSession):
    try:
        # Создаем репозиторий для работы с задачами
        repo = TaskRepository(session)

        async with connection_pool.acquire() as connection:
            async with connection.channel() as channel:
                await channel.declare_queue(
                    QUEUE_NAME, durable=True, arguments={'x-max-priority': 10}
                )

                # Получаем задачу из репозитория
                task = await repo.get(UUID(task_id))

                # Если задача не существует, выходим
                if not task:
                    logger.error(f'Task with ID {task_id} not found.')
                    return

                # Если статус задачи не PENDING, переводим в PENDING
                if task.status != TaskStatus.PENDING:
                    await repo.update_status(task, TaskStatus.PENDING)
                    await session.commit()

                # Публикуем сообщение в очередь
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
    task = None

    try:
        task_uuid = UUID(task_id)
        task = await repo.get(task_uuid)

        logger.info(f'[WORKER] Got task: {task}')

        if not task:
            return

        # переводим NEW -> PENDING
        if task.status == TaskStatus.NEW:
            await repo.update_status(task, TaskStatus.PENDING)
            await session.commit()

        if task.status != TaskStatus.PENDING:
            return

        try:
            if isinstance(task.priority, TaskPriority):
                priority = task.priority.numeric
            else:
                priority = TaskPriority(task.priority).numeric
        except ValueError:
            logger.error(
                f'[WORKER] Invalid priority for task {task.id}: {task.priority}'
            )
            await repo.update_status(
                task,
                TaskStatus.FAILED,
                error=f'Invalid priority: {task.priority}',
            )
            await session.commit()
            return

        await repo.update_status(
            task, TaskStatus.IN_PROGRESS, started_at=datetime.now(timezone.utc)
        )
        await session.commit()
        logger.info(
            f'[WORKER] Task {task.id} started with priority {priority}'
        )

        duration = max(1, 30 - priority * 2)
        logger.info(f'[WORKER] Sleeping for {duration} seconds')
        await asyncio.sleep(duration)

        await repo.update_status(
            task,
            TaskStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc),
            result='Success',
        )
        await session.commit()
        logger.info(f'[WORKER] Task {task.id} completed successfully')

    except Exception as e:
        logger.error(f'Task {task_id} failed: {str(e)}')
        if task:
            await repo.update_status(task, TaskStatus.FAILED, error=str(e))
            await session.commit()
