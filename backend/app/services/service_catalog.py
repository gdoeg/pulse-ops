"""Placeholder infrastructure service catalog for PulseOps."""

from app.ai.base import AIProvider
from app.core.config import Settings
from app.database.session import DatabaseManager
from app.integrations.redis import RedisManager
from app.schemas.service import ServiceDescriptor, ServicesResponse


class ServiceCatalogService:
    """Describe infrastructure integrations without coupling routers to details."""

    def __init__(
        self,
        settings: Settings,
        database: DatabaseManager,
        redis: RedisManager,
        ai_provider: AIProvider,
    ) -> None:
        self._settings = settings
        self._database = database
        self._redis = redis
        self._ai_provider = ai_provider

    def list_services(self) -> ServicesResponse:
        """Return placeholder service descriptors for the current backend runtime."""
        return ServicesResponse(
            services=[
                ServiceDescriptor(
                    name="postgres",
                    kind="database",
                    status="configured",
                    detail=(
                        "Async SQLAlchemy session management is initialized for future PulseOps "
                        f"repositories via {self._settings.async_database_url.split('://', 1)[0]}."
                    ),
                ),
                ServiceDescriptor(
                    name="redis",
                    kind="cache",
                    status="configured",
                    detail=(
                        "Redis connection management is initialized for caching, rate limiting, "
                        "and worker coordination placeholders."
                    ),
                ),
                ServiceDescriptor(
                    name="ai",
                    kind="llm",
                    status=self._ai_provider.status,
                    detail=self._ai_provider.describe(),
                ),
            ]
        )
