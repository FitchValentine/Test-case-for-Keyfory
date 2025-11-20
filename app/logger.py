"""Logging configuration."""
from contextvars import ContextVar

import structlog

from app.config import settings

# Context variable for trace_id
trace_id_context: ContextVar[str | None] = ContextVar("trace_id", default=None)


def configure_logging() -> None:
    """Configure structlog."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.log_level.upper(), structlog.stdlib.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get logger instance."""
    logger = structlog.get_logger(name)
    trace_id = trace_id_context.get()
    if trace_id:
        logger = logger.bind(trace_id=trace_id)
    return logger

