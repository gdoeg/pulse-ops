"""Async SQLAlchemy engine and session management for the worker process."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import WorkerSettings


class WorkerDatabase:
    """Manage an async SQLAlchemy engine dedicated to the worker process."""

    def __init__(self, settings: WorkerSettings) -> None:
        self._settings = settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def initialize(self) -> None:
        """Create the engine and session factory."""
        if self._engine is not None:
            return
        self._engine = create_async_engine(
            self._settings.async_database_url,
            pool_pre_ping=True,
            future=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Dispose of the engine on shutdown."""
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    def session(self) -> AsyncSession:
        """Return a new async session."""
        if self._session_factory is None:
            raise RuntimeError("WorkerDatabase has not been initialized.")
        return self._session_factory()
