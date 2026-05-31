"""Redis-backed task queue for dispatching health-check jobs."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import redis.asyncio as aioredis
from redis.asyncio import Redis

from src.config import WorkerSettings

QUEUE_KEY = "pulseops:check_queue"


class CheckTask:
    """Represents a single health-check task pulled from the Redis queue."""

    __slots__ = ("service_id", "name", "url", "enqueued_at")

    def __init__(
        self,
        *,
        service_id: str,
        name: str,
        url: str,
        enqueued_at: str,
    ) -> None:
        self.service_id = service_id
        self.name = name
        self.url = url
        self.enqueued_at = enqueued_at

    def to_dict(self) -> dict[str, str]:
        return {
            "service_id": self.service_id,
            "name": self.name,
            "url": self.url,
            "enqueued_at": self.enqueued_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> CheckTask:
        return cls(
            service_id=data["service_id"],
            name=data["name"],
            url=data["url"],
            enqueued_at=data["enqueued_at"],
        )


class TaskQueue:
    """Thin Redis-list wrapper for enqueueing and consuming check tasks."""

    def __init__(self, settings: WorkerSettings) -> None:
        self._settings = settings
        self._client: Redis | None = None

    async def initialize(self) -> None:
        """Connect to Redis."""
        if self._client is not None:
            return
        self._client = aioredis.from_url(
            self._settings.redis_dsn,
            decode_responses=True,
            encoding="utf-8",
        )

    async def close(self) -> None:
        """Disconnect from Redis."""
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None

    async def push(self, task: CheckTask) -> None:
        """Enqueue a task at the tail of the Redis list."""
        client = self._require_client()
        await client.rpush(QUEUE_KEY, json.dumps(task.to_dict()))

    async def pop(self, timeout: float = 1.0) -> CheckTask | None:
        """Block-pop a task from the head of the list with a timeout."""
        client = self._require_client()
        result = await client.blpop(QUEUE_KEY, timeout=timeout)
        if result is None:
            return None
        _, raw = result
        return CheckTask.from_dict(json.loads(raw))

    async def queue_length(self) -> int:
        """Return the current number of pending tasks."""
        client = self._require_client()
        return await client.llen(QUEUE_KEY)

    def _require_client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("TaskQueue has not been initialized.")
        return self._client


def make_task(service_id: str, name: str, url: str) -> CheckTask:
    """Construct a check task with the current UTC timestamp."""
    return CheckTask(
        service_id=service_id,
        name=name,
        url=url,
        enqueued_at=datetime.now(UTC).isoformat(),
    )
