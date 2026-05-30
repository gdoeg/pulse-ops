"""Application factory and lifecycle for the PulseOps backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.container import build_container, shutdown_container
from app.core.logging import configure_logging, get_logger
from app.middleware.error_handling import ErrorHandlingMiddleware
from app.middleware.request_timing import RequestTimingMiddleware
from app.routers import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        container = await build_container(settings)
        app.state.container = container

        logger = get_logger(__name__)
        logger.info(
            "pulseops startup complete",
            extra={
                "environment": settings.environment,
                "ai_provider": settings.ai_provider,
            },
        )

        try:
            yield
        finally:
            logger.info(
                "pulseops shutdown started",
                extra={"environment": settings.environment},
            )
            await shutdown_container(container)
            logger.info(
                "pulseops shutdown complete",
                extra={"environment": settings.environment},
            )

    app = FastAPI(
        title=settings.app_name,
        summary="Backend API foundation for PulseOps reliability workflows.",
        description=(
            "PulseOps backend service containing modular routers, service-layer orchestration, "
            "infrastructure integrations, and placeholder endpoints for future QA and "
            "reliability features."
        ),
        version=settings.app_version,
        contact={"name": "PulseOps Engineering", "email": "engineering@pulseops.local"},
        openapi_tags=[
            {"name": "health", "description": "Liveness and readiness probes."},
            {"name": "observability", "description": "Metrics and operational telemetry."},
            {"name": "services", "description": "Infrastructure service placeholders."},
        ],
        lifespan=lifespan,
    )
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.include_router(api_router)
    return app


app = create_app()
