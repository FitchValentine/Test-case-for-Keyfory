"""RabbitMQ producer."""
import json
from typing import Any, Dict

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractConnection, AbstractChannel

from app.config import settings
from app.logger import get_logger, trace_id_context

logger = get_logger(__name__)

# Global connection and channel
_connection: AbstractConnection | None = None
_channel: AbstractChannel | None = None


async def init_rabbitmq() -> None:
    """Initialize RabbitMQ connection."""
    global _connection, _channel
    
    try:
        _connection = await connect_robust(settings.rabbitmq_url)
        _channel = await _connection.channel()
        
        # Declare exchange
        exchange = await _channel.declare_exchange(
            "user_events", type="topic", durable=True
        )
        
        logger.info("rabbitmq_connected")
    except Exception as e:
        logger.error("rabbitmq_connection_error", error=str(e), exc_info=True)
        raise


async def close_rabbitmq() -> None:
    """Close RabbitMQ connection."""
    global _connection, _channel
    
    if _channel:
        await _channel.close()
    if _connection:
        await _connection.close()
    
    logger.info("rabbitmq_disconnected")


async def publish_user_event(event_type: str, data: Dict[str, Any]) -> None:
    """Publish user event to RabbitMQ."""
    global _channel
    
    if not _channel:
        logger.warning("rabbitmq_channel_not_initialized")
        return
    
    try:
        trace_id = trace_id_context.get()
        
        event_data = {
            "event_type": event_type,
            "data": data,
            "trace_id": trace_id,
        }
        
        message = Message(
            body=json.dumps(event_data).encode(),
            headers={"trace_id": trace_id} if trace_id else {},
        )
        
        exchange = await _channel.get_exchange("user_events")
        await exchange.publish(
            message,
            routing_key=event_type,
        )
        
        logger.info(
            "event_published",
            event_type=event_type,
            user_id=data.get("user_id"),
            trace_id=trace_id,
        )
    except Exception as e:
        logger.error(
            "error_publishing_event",
            event_type=event_type,
            error=str(e),
            exc_info=True,
        )

