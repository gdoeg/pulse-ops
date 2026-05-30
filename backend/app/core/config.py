"""Environment-driven application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and local .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(
        default="PulseOps API",
        validation_alias=AliasChoices("APP_NAME"),
    )
    app_version: str = Field(
        default="0.1.0",
        validation_alias=AliasChoices("APP_VERSION"),
    )
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("PULSEOPS_ENV"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL"),
    )
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
    ai_provider: Literal["mock", "openai", "groq"] = Field(
        default="mock",
        validation_alias=AliasChoices("AI_PROVIDER"),
    )
    ai_model: str = Field(
        default="mock-local-model",
        validation_alias=AliasChoices("AI_MODEL"),
    )
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY"),
    )
    groq_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("GROQ_API_KEY"),
    )

    @property
    def async_database_url(self) -> str:
        """Return the SQLAlchemy async PostgreSQL URL."""
        if self.database_url:
            return self._normalize_database_scheme(self.database_url)

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
    def _normalize_database_scheme(database_url: str) -> str:
        if database_url.startswith("postgresql+psycopg://"):
            return database_url
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return database_url


@lru_cache
def get_settings() -> Settings:
    """Cache settings to provide stable dependency injection across requests."""
    return Settings()
