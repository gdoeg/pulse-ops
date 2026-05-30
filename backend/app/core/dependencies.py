"""FastAPI dependency providers for shared infrastructure and services."""

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider
from app.core.config import Settings
from app.core.container import AppContainer
from app.database.session import DatabaseManager
from app.integrations.redis import RedisManager
from app.observability.metrics import AppMetrics
from app.services.health import HealthService
from app.services.metrics import MetricsService
from app.services.service_catalog import ServiceCatalogService


def get_container(request: Request) -> AppContainer:
    """Return the application container stored on app state."""
    return request.app.state.container


def get_settings(container: AppContainer = Depends(get_container)) -> Settings:
    """Resolve application settings from the shared container."""
    return container.settings


def get_metrics(container: AppContainer = Depends(get_container)) -> AppMetrics:
    """Resolve the in-memory metrics registry."""
    return container.metrics


def get_database(container: AppContainer = Depends(get_container)) -> DatabaseManager:
    """Resolve the database manager."""
    return container.database


def get_redis(container: AppContainer = Depends(get_container)) -> RedisManager:
    """Resolve the Redis manager."""
    return container.redis


def get_ai_provider(container: AppContainer = Depends(get_container)) -> AIProvider:
    """Resolve the configured AI provider implementation."""
    return container.ai_provider


async def get_db_session(
    database: DatabaseManager = Depends(get_database),
) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped SQLAlchemy session for future repository layers."""
    async with database.session() as session:
        yield session


def get_health_service(settings: Settings = Depends(get_settings)) -> HealthService:
    """Resolve the health service."""
    return HealthService(settings)


def get_metrics_service(metrics: AppMetrics = Depends(get_metrics)) -> MetricsService:
    """Resolve the metrics service."""
    return MetricsService(metrics)


def get_service_catalog_service(
    settings: Settings = Depends(get_settings),
    database: DatabaseManager = Depends(get_database),
    redis: RedisManager = Depends(get_redis),
    ai_provider: AIProvider = Depends(get_ai_provider),
) -> ServiceCatalogService:
    """Resolve the infrastructure service catalog service."""
    return ServiceCatalogService(settings, database, redis, ai_provider)
