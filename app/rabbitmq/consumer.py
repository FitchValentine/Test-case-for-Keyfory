"""RabbitMQ consumer."""
import asyncio
import json
from contextvars import ContextVar
from typing import Optional

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream.rabbit.annotations import RabbitMessage

from app.config import settings
from app.logger import get_logger, trace_id_context

logger = get_logger(__name__)

# Context variable for trace_id in consumer
consumer_trace_id_context: ContextVar[str | None] = ContextVar("trace_id", default=None)

# Create broker
broker = RabbitBroker(settings.rabbitmq_url)

# Create app
app = FastStream(broker)

# Task for running consumer
_consumer_task: Optional[asyncio.Task] = None


@broker.subscriber("user.created", exchange="user_events")
@broker.subscriber("user.updated", exchange="user_events")
@broker.subscriber("user.deleted", exchange="user_events")
async def handle_user_event(
    message: RabbitMessage,
    routing_key: str,
) -> None:
    """Handle user events from RabbitMQ."""
    trace_id = None
    try:
        # Extract trace_id from message headers
        if message.headers:
            trace_id = message.headers.get("trace_id")
        
        # Set trace_id in context
        if trace_id:
            trace_id_context.set(trace_id)
            consumer_trace_id_context.set(trace_id)
        
        # Parse message body
        body = json.loads(message.body.decode())
        event_data = body.get("data", {})
        user_id = event_data.get("user_id")
        
        # Log event with trace_id
        log = logger.bind(trace_id=trace_id)
        log.info(
            "event_received",
            event_type=routing_key,
            user_id=user_id,
            trace_id=trace_id,
        )
        
        # Here you can add business logic for handling events
        # For example: send notifications, update caches, etc.
        
    except Exception as e:
        log = logger.bind(trace_id=trace_id or trace_id_context.get())
        log.error(
            "error_handling_event",
            routing_key=routing_key,
            error=str(e),
            exc_info=True,
        )


async def _run_consumer() -> None:
    """Run consumer in background."""
    try:
        await app.run()
    except Exception as e:
        logger.error("consumer_runtime_error", error=str(e), exc_info=True)


async def setup_consumer() -> None:
    """Setup and start RabbitMQ consumer."""
    global _consumer_task
    
    try:
        logger.info("starting_rabbitmq_consumer")
        # Start consumer in background task
        _consumer_task = asyncio.create_task(_run_consumer())
        logger.info("rabbitmq_consumer_started")
    except Exception as e:
        logger.error("rabbitmq_consumer_error", error=str(e), exc_info=True)
        raise


async def close_consumer() -> None:
    """Close RabbitMQ consumer."""
    global _consumer_task
    
    try:
        if _consumer_task:
            _consumer_task.cancel()
            try:
                await _consumer_task
            except asyncio.CancelledError:
                pass
        
        await broker.close()
        logger.info("rabbitmq_consumer_closed")
    except Exception as e:
        logger.error("rabbitmq_consumer_close_error", error=str(e), exc_info=True)

