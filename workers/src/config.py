"""Environment-driven settings for the PulseOps monitoring worker."""

from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("PULSEOPS_ENV"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL"),
    )

    # PostgreSQL
    database_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    postgres_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("POSTGRES_HOST"),
    )
    postgres_port: int = Field(
        default=5432,
        validation_alias=AliasChoices("POSTGRES_PORT"),
    )
    postgres_db: str = Field(
        default="pulseops",
        validation_alias=AliasChoices("POSTGRES_DB"),
    )
    postgres_user: str = Field(
        default="pulseops",
        validation_alias=AliasChoices("POSTGRES_USER"),
    )
    postgres_password: SecretStr = Field(
        default=SecretStr("pulseops"),
        validation_alias=AliasChoices("POSTGRES_PASSWORD"),
    )

    # Redis
    redis_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("REDIS_URL"),
    )
    redis_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("REDIS_HOST"),
    )
    redis_port: int = Field(
        default=6379,
        validation_alias=AliasChoices("REDIS_PORT"),
    )

    # Worker behaviour
    worker_concurrency: int = Field(
        default=4,
        ge=1,
        le=32,
        validation_alias=AliasChoices("WORKER_CONCURRENCY"),
    )
    scheduler_interval_seconds: float = Field(
        default=5.0,
        ge=1.0,
        validation_alias=AliasChoices("SCHEDULER_INTERVAL_SECONDS"),
    )
    http_timeout_seconds: float = Field(
        default=10.0,
        ge=1.0,
        validation_alias=AliasChoices("HTTP_TIMEOUT_SECONDS"),
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        validation_alias=AliasChoices("MAX_RETRIES"),
    )
    degraded_threshold_ms: float = Field(
        default=5_000.0,
        ge=100.0,
        validation_alias=AliasChoices("DEGRADED_THRESHOLD_MS"),
    )

    @property
    def async_database_url(self) -> str:
        """Return the SQLAlchemy async PostgreSQL URL."""
        if self.database_url:
            return self._normalize_scheme(self.database_url)
        password = self.postgres_password.get_secret_value()
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    @property
    def redis_dsn(self) -> str:
        """Return the Redis connection URL."""
        if self.redis_url:
            return self.redis_url
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def _normalize_scheme(url: str) -> str:
        if url.startswith("postgresql+psycopg://"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> WorkerSettings:
    """Return cached worker settings."""
    return WorkerSettings()
