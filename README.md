# REST API для управления пользователями

REST API на базе LiteStar (Python 3.12) с CRUD-операциями для таблицы user в PostgreSQL.

## Возможности

-  Swagger документация
-  CRUD операции для пользователей
-  Логирование с structlog и trace_id
-  Интеграция с RabbitMQ (producer/consumer)
-  Docker Compose для инфраструктуры

##  Требования

- Python 3.12+
- Poetry 1.8.3+
- Docker и Docker Compose

##  Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Test-case-for-Keyfory
```

### 2. Установка зависимостей

```bash
poetry install
```

### 3. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/userdb
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
APP_NAME=user-management-api
LOG_LEVEL=INFO
```

### 4. Запуск инфраструктуры (PostgreSQL и RabbitMQ)

```bash
docker-compose up -d
```

Проверьте, что контейнеры запущены:

```bash
docker-compose ps
```

### 5. Применение миграций базы данных

Создайте первую миграцию:

```bash
poetry run alembic revision --autogenerate -m "Initial migration"
```

Примените миграции:

```bash
poetry run alembic upgrade head
```

Примечание: Если используете advanced-alchemy, миграции можно также создавать через:

```bash
poetry run litestar db revision --autogenerate -m "Initial migration"
poetry run litestar db upgrade
```

### 6. Запуск приложения

```bash
poetry run litestar run --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`


##  API Endpoints

### Пользователи

- `POST /api/v1/users` - Создать пользователя
- `GET /api/v1/users` - Получить список пользователей
- `GET /api/v1/users/{user_id}` - Получить пользователя по ID
- `PUT /api/v1/users/{user_id}` - Обновить пользователя
- `DELETE /api/v1/users/{user_id}` - Удалить пользователя

### Примеры запросов

#### Создание пользователя

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: my-trace-id-123" \
  -d '{
    "name": "Иван",
    "surname": "Иванов",
    "password": "secret123"
  }'
```

#### Получение списка пользователей

```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "X-Request-Id: my-trace-id-123"
```

#### Получение пользователя по ID

```bash
curl -X GET http://localhost:8000/api/v1/users/1 \
  -H "X-Request-Id: my-trace-id-123"
```

#### Обновление пользователя

```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: my-trace-id-123" \
  -d '{
    "name": "Петр",
    "surname": "Петров"
  }'
```

#### Удаление пользователя

```bash
curl -X DELETE http://localhost:8000/api/v1/users/1 \
  -H "X-Request-Id: my-trace-id-123"
```

## 🔍 Логирование и Trace ID


- Если в заголовке запроса есть `X-Request-Id`, он используется как `trace_id`
- Если заголовка нет, генерируется новый UUID
- `trace_id` добавляется в каждую лог-запись
- `trace_id` возвращается в заголовке ответа `X-Trace-Id`

### Пример логов

```json
{
  "event": "request_started",
  "method": "POST",
  "path": "/api/v1/users",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00.123456Z"
}
```

## 🐰 RabbitMQ

Приложение публикует события в RabbitMQ при создании, обновлении и удалении пользователей:

- `user.created` - при создании пользователя
- `user.updated` - при обновлении пользователя
- `user.deleted` - при удалении пользователя

Consumer обрабатывает эти события и логирует их с сохранением `trace_id`.

### Управление RabbitMQ

RabbitMQ Management UI доступен по адресу: `http://localhost:15672`

- Логин: `guest`
- Пароль: `guest`

## 🏗️ Архитектура

```
app/
├── config.py              # Конфигурация приложения
├── main.py                # Точка входа приложения
├── logger.py              # Настройка логирования
├── controllers/           # HTTP контроллеры
│   └── user.py
├── services/              # Бизнес-логика
│   └── user.py
├── repositories/          # Репозитории для работы с БД
│   └── user.py
├── schemas/               # Схемы данных (msgspec)
│   └── user.py
├── db/                    # База данных
│   ├── base.py
│   ├── models.py
│   └── migrations/
├── middleware/            # Middleware
│   └── trace_id.py
└── rabbitmq/              # RabbitMQ интеграция
    ├── producer.py
    └── consumer.py
```


## 🐳 Docker

Для остановки инфраструктуры:

```bash
docker-compose down
```

Для остановки и удаления данных:

```bash
docker-compose down -v
```

