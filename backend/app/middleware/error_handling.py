"""Global API error handling middleware."""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import PulseOpsError
from app.core.logging import get_logger
from app.schemas.error import ErrorResponse

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and convert them into consistent API responses."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except PulseOpsError as exc:
            self._record_error(request)
            logger.warning(
                exc.message,
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": exc.status_code,
                },
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=getattr(request.state, "request_id", None),
                ).model_dump(),
            )
        except Exception:
            self._record_error(request)
            logger.exception(
                "unhandled application error",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": 500,
                },
            )
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    code="internal_server_error",
                    message="An unexpected error occurred.",
                    request_id=getattr(request.state, "request_id", None),
                ).model_dump(),
            )

    @staticmethod
    def _record_error(request: Request) -> None:
        container = getattr(request.app.state, "container", None)
        if container is not None:
            container.metrics.record_error()
