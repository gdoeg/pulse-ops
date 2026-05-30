"""Application container used during startup and dependency injection."""

from dataclasses import dataclass

from app.ai.base import AIProvider
from app.ai.factory import create_ai_provider
from app.core.config import Settings
from app.database.session import DatabaseManager
from app.integrations.redis import RedisManager
from app.observability.metrics import AppMetrics


@dataclass(slots=True)
class AppContainer:
    """Shared infrastructure components initialized during application startup."""

    settings: Settings
    metrics: AppMetrics
    database: DatabaseManager
    redis: RedisManager
    ai_provider: AIProvider


async def build_container(settings: Settings) -> AppContainer:
    """Construct long-lived application dependencies."""
    metrics = AppMetrics()
    database = DatabaseManager(settings)
    redis = RedisManager(settings)
    ai_provider = create_ai_provider(settings)

    await database.initialize()
    await redis.initialize()

    return AppContainer(
        settings=settings,
        metrics=metrics,
        database=database,
        redis=redis,
        ai_provider=ai_provider,
    )


async def shutdown_container(container: AppContainer) -> None:
    """Gracefully close infrastructure clients during shutdown."""
    await container.database.close()
    await container.redis.close()
