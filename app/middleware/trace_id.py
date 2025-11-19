"""Trace ID middleware."""
import time
import uuid
from typing import Callable

from litestar import Request
from litestar.middleware import AbstractMiddleware

from app.logger import get_logger, trace_id_context

logger = get_logger(__name__)


class TraceIDMiddleware(AbstractMiddleware):
    """Middleware for trace ID handling and request logging."""

    async def __call__(
        self, scope: dict, receive: Callable, send: Callable
    ) -> None:
        """Process request with trace ID."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Get or generate trace_id
        trace_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        trace_id_context.set(trace_id)
        
        # Bind trace_id to logger
        log = logger.bind(trace_id=trace_id)
        
        # Log request start
        start_time = time.time()
        log.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
        )
        
        status_code = 200
        
        # Intercept response to add trace_id header
        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            
            if message["type"] == "http.response.start":
                status_code = message["status"]
                # Add trace_id to response headers
                headers = list(message.get("headers", []))
                headers.append((b"x-trace-id", trace_id.encode()))
                message["headers"] = headers
            
            await send(message)
        
        # Process request
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Log error
            log.error(
                "request_error",
                method=request.method,
                path=request.url.path,
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request completion
            log.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
            )

