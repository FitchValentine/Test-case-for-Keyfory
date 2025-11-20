"""Application configuration."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/userdb"
    )

    # RabbitMQ
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    # Application
    app_name: str = os.getenv("APP_NAME", "user-management-api")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # API
    api_prefix: str = "/api/v1"


settings = Settings()

