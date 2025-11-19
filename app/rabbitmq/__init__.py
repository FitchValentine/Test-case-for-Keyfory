"""RabbitMQ module."""
from app.rabbitmq.consumer import setup_consumer
from app.rabbitmq.producer import publish_user_event

__all__ = ["setup_consumer", "publish_user_event"]

