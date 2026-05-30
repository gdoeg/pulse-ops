"""Metrics endpoints for observability integrations."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.core.dependencies import get_metrics_service
from app.services.metrics import MetricsService

router = APIRouter(tags=["observability"])
MetricsServiceDependency = Annotated[MetricsService, Depends(get_metrics_service)]


@router.get(
    "/metrics",
    summary="Prometheus metrics endpoint",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/plain": {}}}},
)
async def metrics(service: MetricsServiceDependency) -> PlainTextResponse:
    """Return metrics emitted by the current API process."""
    return PlainTextResponse(
        content=service.render(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
