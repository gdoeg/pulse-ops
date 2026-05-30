"""Healthcheck routes for API liveness and readiness."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_health_service
from app.schemas.health import HealthResponse
from app.services.health import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Application liveness probe")
async def liveness(
    service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Return the process liveness state for load balancers and probes."""
    return service.liveness()


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    summary="Application readiness probe",
)
async def readiness(
    service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Return the startup readiness state for backwards-compatible checks."""
    return service.readiness()
