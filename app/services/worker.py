import asyncio
import json

import aio_pika  # Не забывай про этот импорт
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logger import logger
from app.db.database import AsyncSessionLocal
from app.services.task_service import process_task

QUEUE_NAME = 'tasks_queue'


async def process_messages(connection: AbstractRobustConnection):
    async with connection:
        # Создаем канал для взаимодействия с RabbitMQ
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=5)

        # Объявляем очередь с указанными аргументами
        queue = await channel.declare_queue(
            QUEUE_NAME, durable=True, arguments={'x-max-priority': 10}
        )
        logger.info(
            f"Queue '{QUEUE_NAME}' declared and ready to consume messages."
        )

        # Итерируем по сообщениям в очереди
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logger.info(f"Received message: {message.body.decode()}")
                try:
                    # Создаем сессию с базой данных
                    async with AsyncSessionLocal() as session:
                        # Преобразуем тело сообщения в Python-словарь
                        data = json.loads(message.body.decode())
                        task_id = data.get('task_id')

                        # Обрабатываем задачу с данным task_id
                        await process_task(session, task_id)
                        await session.commit()

                        # После успешной обработки подтверждаем получение сообщения
                        await message.ack()
                        logger.info(f"Task {task_id} processed successfully.")
                except Exception as e:
                    # Если произошла ошибка, отклоняем сообщение с повторной попыткой
                    logger.error(f"Error processing message: {str(e)}")
                    await message.nack(requeue=True)
                    # Пауза перед следующей попыткой
                    await asyncio.sleep(5)


async def main():
    # Создаем подключение к RabbitMQ
    while True:
        try:
            connection = await aio_pika.connect_robust(
                settings.rabbitmq_url,
                timeout=30,
                client_properties={'connection_name': 'worker'},
            )
            logger.info("Connected to RabbitMQ.")
            # Запускаем процесс обработки сообщений
            await process_messages(connection)
        except Exception as e:
            logger.error(
                f"Connection error: {str(e)}, retrying in 10 seconds..."
            )
            await asyncio.sleep(10)


if __name__ == '__main__':
    # Запускаем главный цикл для воркера
    asyncio.run(main())
