"""Healthcheck endpoints used by local and production probes."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Liveness healthcheck placeholder")
def liveness() -> dict[str, str]:
    """Placeholder liveness endpoint for orchestration probes."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness healthcheck placeholder")
def readiness() -> dict[str, str]:
    """Placeholder readiness endpoint for dependency-aware checks."""
    return {"status": "ready"}
