"""Async SQLAlchemy engine and session management."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


class DatabaseManager:
    """Manage the application's async SQLAlchemy resources."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def initialize(self) -> None:
        """Initialize the async engine and session factory during startup."""
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
        """Dispose of the SQLAlchemy engine during shutdown."""
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    def session(self) -> AsyncIterator[AsyncSession]:
        """Create a new async database session for repository usage."""
        if self._session_factory is None:
            raise RuntimeError("Database manager has not been initialized.")
        return self._session_factory()
