# Async Task Service 🚀

Микросервис для управления асинхронными задачами с приоритезацией.

## Требования ⚙️

- Docker
- Docker Compose
- Python
- PostgreSQL
- RabbitMQ

## Быстрый старт через Docker 🐳

### Сборка и запуск

```
docker-compose up --build -d
```

### Проверить статус сервисов

```
docker-compose ps
```

### Остановка

```
docker-compose down
```

## Миграции базы данных 🗄️

### Создать новую миграцию

```
alembic revision --autogenerate -m "Описание изменений"
```

### Применить миграции

```
alembic upgrade head
```

## Примеры API запросов 📡

### Создание задачи

```
POST /api/v1/tasks
Content-Type: application/json

{
  "name": "Обработать данные",
  "description": "Анализ пользовательской активности",
  "priority": "HIGH"
}
```

### Ответ:

```
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Обработать данные",
  "status": "PENDING",
  "priority": "HIGH",
  "created_at": "2024-03-15T10:30:00Z"
}
```

### Получение списка задач

```
GET /api/v1/tasks?status=COMPLETED&page=2&size=10
```

### Ответ:

```
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Резервное копирование",
      "status": "COMPLETED",
      "priority": "MEDIUM",
      "created_at": "2024-03-14T15:45:00Z"
    }
  ],
  "total": 25,
  "page": 2,
  "size": 10
}
```

### Отмена задачи

```
DELETE /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000
```

## Тестирование 🧪

### Запуск всех тестов

```
pytest
```

## Переменные окружения ⚙️

### .env файл:

```
DEBUG=True
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=tasks_db
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/tasks_db
```

## Структура проекта 📂

```
.
├── alembic/              # Миграции БД
├── app/
│   ├── core/             # Базовые настройки
│   ├── db/               # Работа с БД
│   ├── models/           # Модели данных
│   ├── repositories/     # Репозитории данных
│   ├── routers/          # API роутеры
│   ├── schemas/          # Pydantic схемы
│   └── services/         # Фоновые сервисы
├── tests/                # Тесты
└── docker-compose.yml    # Конфигурация Docker
```
