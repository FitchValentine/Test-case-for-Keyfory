"""Main application."""
from contextlib import asynccontextmanager

from litestar import Litestar, Router
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from app.config import settings
from app.controllers.user import UserController
from app.db.base import sqlalchemy_config
from app.logger import configure_logging, get_logger
from app.middleware.trace_id import TraceIDMiddleware
from app.rabbitmq.consumer import close_consumer, setup_consumer
from app.rabbitmq.producer import close_rabbitmq, init_rabbitmq

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: Litestar):
    """Application lifespan manager."""
    # Startup
    logger.info("application_starting")
    
    # Initialize RabbitMQ producer
    try:
        await init_rabbitmq()
    except Exception as e:
        logger.error("failed_to_init_rabbitmq", error=str(e), exc_info=True)
        # Continue even if RabbitMQ fails
    
    # Initialize RabbitMQ consumer
    try:
        await setup_consumer()
    except Exception as e:
        logger.error("failed_to_setup_consumer", error=str(e), exc_info=True)
        # Continue even if consumer fails
    
    logger.info("application_started")
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")
    
    try:
        await close_consumer()
    except Exception as e:
        logger.error("error_closing_consumer", error=str(e), exc_info=True)
    
    try:
        await close_rabbitmq()
    except Exception as e:
        logger.error("error_closing_rabbitmq", error=str(e), exc_info=True)
    
    logger.info("application_shutdown")


# Configure logging
configure_logging()

# Create router
api_router = Router(
    path=settings.api_prefix,
    route_handlers=[UserController],
)

# Create application
app = Litestar(
    route_handlers=[api_router],
    plugins=[sqlalchemy_config],
    middleware=[TraceIDMiddleware],
    openapi_config=OpenAPIConfig(
        title=settings.app_name,
        version="1.0.0",
        description="REST API for user management with LiteStar",
    ),
    cors_config=CORSConfig(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    lifespan=lifespan,
)

