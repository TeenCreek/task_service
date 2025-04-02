import asyncio
import json

import aio_pika
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logger import logger
from app.services.task_service import process_task


async def main():
    engine = create_async_engine(settings.database_url)
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("tasks_queue", durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        async with engine.begin() as session:
                            await process_task(session, data["task_id"])
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")


if __name__ == "__main__":
    asyncio.run(main())
