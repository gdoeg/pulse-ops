"""FastAPI dependency providers for shared infrastructure and services."""

from collections.abc import AsyncIterator
from typing import Annotated

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
from app.services.monitor import MonitorService
from app.services.service_catalog import ServiceCatalogService


def get_container(request: Request) -> AppContainer:
    """Return the application container stored on app state."""
    return request.app.state.container


ContainerDependency = Annotated[AppContainer, Depends(get_container)]


def get_settings(container: ContainerDependency) -> Settings:
    """Resolve application settings from the shared container."""
    return container.settings


SettingsDependency = Annotated[Settings, Depends(get_settings)]


def get_metrics(container: ContainerDependency) -> AppMetrics:
    """Resolve the in-memory metrics registry."""
    return container.metrics


MetricsDependency = Annotated[AppMetrics, Depends(get_metrics)]


def get_database(container: ContainerDependency) -> DatabaseManager:
    """Resolve the database manager."""
    return container.database


DatabaseDependency = Annotated[DatabaseManager, Depends(get_database)]


def get_redis(container: ContainerDependency) -> RedisManager:
    """Resolve the Redis manager."""
    return container.redis


RedisDependency = Annotated[RedisManager, Depends(get_redis)]


def get_ai_provider(container: ContainerDependency) -> AIProvider:
    """Resolve the configured AI provider implementation."""
    return container.ai_provider


AIProviderDependency = Annotated[AIProvider, Depends(get_ai_provider)]


async def get_db_session(database: DatabaseDependency) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped SQLAlchemy session for repository layers."""
    async with database.session() as session:
        yield session


def get_health_service(settings: SettingsDependency) -> HealthService:
    """Resolve the health service."""
    return HealthService(settings)


def get_metrics_service(metrics: MetricsDependency) -> MetricsService:
    """Resolve the metrics service."""
    return MetricsService(metrics)


def get_service_catalog_service(
    settings: SettingsDependency,
    database: DatabaseDependency,
    redis: RedisDependency,
    ai_provider: AIProviderDependency,
) -> ServiceCatalogService:
    """Resolve the infrastructure service catalog service."""
    return ServiceCatalogService(settings, database, redis, ai_provider)


def get_monitor_service() -> MonitorService:
    """Resolve the monitoring service (stateless, created per request)."""
    return MonitorService()
