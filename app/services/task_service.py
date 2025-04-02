import asyncio
import json
from datetime import datetime
from uuid import UUID  # Import UUID for conversion

import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models.task import TaskStatus  # Import TaskStatus for status checks
from app.repositories.task import TaskRepository

QUEUE_NAME = "tasks_queue"


async def publish_task(task_id: str):
    try:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(QUEUE_NAME, durable=True)

            message = aio_pika.Message(
                body=json.dumps({"task_id": task_id}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await channel.default_exchange.publish(
                message, routing_key=QUEUE_NAME
            )
    except Exception as e:
        logger.error(f"Failed to publish task {task_id}: {e}")
        raise


async def process_task(session: AsyncSession, task_id: str):
    repo = TaskRepository(session)
    try:
        task_uuid = UUID(task_id)  # Convert task_id to UUID
    except ValueError:
        logger.error(f"Invalid task_id format: {task_id}")
        return

    async with session.begin():
        task = await repo.get(task_uuid)  # Use the converted UUID
        if not task or task.status != TaskStatus.PENDING:
            return

        try:
            await repo.update_status(
                task, TaskStatus.IN_PROGRESS, started_at=datetime.utcnow()
            )

            # Simulate work
            await asyncio.sleep(5)

            await repo.update_status(
                task,
                TaskStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result="Task processed successfully",
            )
        except Exception as e:
            await repo.update_status(
                task,
                TaskStatus.FAILED,
                completed_at=datetime.utcnow(),
                error=str(e),
            )
            logger.error(f"Task {task_id} failed: {e}")
