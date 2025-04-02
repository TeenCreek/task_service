from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field('Async Task Service', env='PROJECT_NAME')
    debug: bool = Field(True, env='DEBUG')

    db_host: str = Field('db', env='DB_HOST')
    db_port: int = Field(5432, env='DB_PORT')
    db_user: str = Field('postgres', env='DB_USER')
    db_password: str = Field('password', env='DB_PASSWORD')
    db_name: str = Field('tasks_db', env='DB_NAME')

    rabbitmq_url: str = Field(
        'amqp://guest:guest@rabbitmq:5672/', env='RABBITMQ_URL'
    )

    @property
    def database_url(self) -> str:
        """Асинхронный URL базы данных."""
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def sync_database_url(self) -> str:
        """Синхронный URL базы данных (для Alembic)."""
        return f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    model_config = SettingsConfigDict(
        env_file='.env', case_sensitive=True, extra='ignore'
    )


settings = Settings()
