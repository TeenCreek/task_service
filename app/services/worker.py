import asyncio
import json

import aio_pika

from app.core.config import settings
from app.core.logger import logger
from app.db.session import get_db_session
from app.services.task_service import process_task

QUEUE_NAME = 'tasks_queue'


async def main():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True,
        arguments={'x-max-priority': 10},
    )
    logger.info(
        f"Queue '{QUEUE_NAME}' declared and ready to consume messages."
    )

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body)
                task_id = data.get('task_id')
                logger.info(f"Received message: {data}")

                async for session in get_db_session():
                    await process_task(session, task_id)
                    logger.info(f"Task {task_id} processed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
