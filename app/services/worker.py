import asyncio
import json

import aio_pika
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logger import logger
from app.db.database import AsyncSessionLocal
from app.services.task_service import process_task


async def main():
    engine = create_async_engine(settings.database_url)
    connection = await aio_pika.connect_robust(
        settings.rabbitmq_url, timeout=10
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=5)

        queue = await channel.declare_queue(
            'tasks_queue', durable=True, arguments={'x-max-priority': 10}
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        async with AsyncSessionLocal() as session:
                            await process_task(session, data['task_id'])
                    except Exception as e:
                        logger.error(f'Error processing message: {str(e)}')
                        await message.nack()


if __name__ == '__main__':
    asyncio.run(main())
