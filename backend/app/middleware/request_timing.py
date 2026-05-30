"""Middleware for request timing, correlation IDs, and access logs."""

import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Measure request latency and record structured access logs."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", uuid4().hex)
        request.state.request_id = request_id

        started_at = time.perf_counter()
        response = await call_next(request)
        duration_seconds = time.perf_counter() - started_at
        duration_ms = round(duration_seconds * 1000, 3)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_seconds:.6f}"

        container = getattr(request.app.state, "container", None)
        if container is not None:
            container.metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=duration_seconds,
            )

        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
