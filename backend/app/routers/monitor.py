"""Service monitoring API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_monitor_service
from app.schemas.monitor import (
    CheckHistoryResponse,
    IncidentListResponse,
    MonitoredServiceCreate,
    MonitoredServiceListResponse,
    MonitoredServiceResponse,
    UptimeResponse,
)
from app.services.monitor import MonitorService

router = APIRouter(prefix="/monitor", tags=["monitoring"])

MonitorServiceDependency = Annotated[MonitorService, Depends(get_monitor_service)]
DbSessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


@router.post(
    "/services",
    response_model=MonitoredServiceResponse,
    status_code=201,
    summary="Register a service for monitoring",
)
async def register_service(
    payload: MonitoredServiceCreate,
    service: MonitorServiceDependency,
    session: DbSessionDependency,
) -> MonitoredServiceResponse:
    """Register a new service endpoint to be polled by the monitoring worker."""
    return await service.register_service(session, payload)


@router.get(
    "/services",
    response_model=MonitoredServiceListResponse,
    summary="List all registered services",
)
async def list_services(
    service: MonitorServiceDependency,
    session: DbSessionDependency,
) -> MonitoredServiceListResponse:
    """Return all services registered with the monitoring engine."""
    return await service.list_monitored_services(session)


@router.get(
    "/services/{service_id}",
    response_model=MonitoredServiceResponse,
    summary="Get a registered service",
)
async def get_service(
    service_id: uuid.UUID,
    service: MonitorServiceDependency,
    session: DbSessionDependency,
) -> MonitoredServiceResponse:
    """Return a single monitored service by its identifier."""
    return await service.get_service(session, service_id)


@router.get(
    "/services/{service_id}/checks",
    response_model=CheckHistoryResponse,
    summary="Get recent health-check results",
)
async def get_check_history(
    service_id: uuid.UUID,
    service: MonitorServiceDependency,
    session: DbSessionDependency,
    limit: int = Query(default=100, ge=1, le=1000, description="Max number of results to return."),
) -> CheckHistoryResponse:
    """Return the most recent health-check results for a service."""
    return await service.get_check_history(session, service_id, limit=limit)


@router.get(
    "/services/{service_id}/uptime",
    response_model=UptimeResponse,
    summary="Get uptime statistics",
)
async def get_uptime(
    service_id: uuid.UUID,
    service: MonitorServiceDependency,
    session: DbSessionDependency,
    window_hours: int = Query(
        default=24,
        ge=1,
        le=720,
        description="Rolling window in hours (1 – 720).",
    ),
) -> UptimeResponse:
    """Return uptime percentage and response-time averages for a service."""
    return await service.calculate_uptime(session, service_id, window_hours=window_hours)


@router.get(
    "/services/{service_id}/incidents",
    response_model=IncidentListResponse,
    summary="Get incident history",
)
async def get_incidents(
    service_id: uuid.UUID,
    service: MonitorServiceDependency,
    session: DbSessionDependency,
    open_only: bool = Query(default=False, description="When true, return only open incidents."),
) -> IncidentListResponse:
    """Return incidents (open and resolved) for a service."""
    return await service.get_incidents(session, service_id, open_only=open_only)
