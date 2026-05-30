"""Business logic for health and readiness reporting."""

from app.core.config import Settings
from app.schemas.health import HealthResponse


class HealthService:
    """Produce health payloads without embedding infrastructure logic in routers."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def liveness(self) -> HealthResponse:
        """Return a liveness response for orchestration probes."""
        return HealthResponse(
            status="ok",
            service=self._settings.app_name,
            environment=self._settings.environment,
            version=self._settings.app_version,
        )

    def readiness(self) -> HealthResponse:
        """Return a readiness placeholder while repositories and workers evolve."""
        return HealthResponse(
            status="ready",
            service=self._settings.app_name,
            environment=self._settings.environment,
            version=self._settings.app_version,
        )
