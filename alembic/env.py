import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context
from app.core.config import settings
from app.db.database import Base

config = context.config
section = config.config_ini_section

db_url = settings.sync_database_url
config.set_section_option(section, "sqlalchemy.url", db_url)

sync_engine = create_engine(db_url)

target_metadata = Base.metadata


def run_migrations_online():
    """Запуск миграций в режиме онлайн."""

    with sync_engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
