# alembic/env.py
import os
import sys
from logging.config import fileConfig

from alembic import context
from app.db.database import Base  # Импортируем Base из app.db.database
from app.db.database import sync_engine
from app.models import Task  # Импортируем модель Task

# Добавляем корень проекта в путь поиска модулей
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)

config = context.config
section = config.config_ini_section
db_url = config.get_section_option(section, "sqlalchemy.url")
engine = sync_engine  # Используем синхронный движок для миграций
target_metadata = (
    Base.metadata
)  # Это всё метаданные, включая все импорты моделей


def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            **config.get_section(section)
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
