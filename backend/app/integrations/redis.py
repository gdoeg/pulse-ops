"""Redis connection layer used by services and workers."""

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import Settings


class RedisManager:
    """Create and close the shared Redis client."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Redis | None = None

    async def initialize(self) -> None:
        """Initialize the Redis client during startup."""
        if self._client is not None:
            return
        self._client = redis.from_url(
            self._settings.redis_dsn,
            decode_responses=True,
            encoding="utf-8",
        )

    async def close(self) -> None:
        """Close the Redis client during shutdown."""
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None

    @property
    def client(self) -> Redis:
        """Expose the shared Redis client for future caching and queue features."""
        if self._client is None:
            raise RuntimeError("Redis manager has not been initialized.")
        return self._client
