"""Pydantic schemas for the service monitoring API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class MonitoredServiceCreate(BaseModel):
    """Payload for registering a new service with the monitoring engine."""

    name: str = Field(description="Human-readable service name.", min_length=1, max_length=255)
    url: HttpUrl = Field(description="Health-check URL to poll.")
    check_interval_seconds: int = Field(
        default=60,
        ge=10,
        le=86400,
        description="Polling interval in seconds (10 – 86400).",
    )
    enabled: bool = Field(default=True, description="Whether the service is actively monitored.")


class MonitoredServiceResponse(BaseModel):
    """Full representation of a registered service."""

    id: uuid.UUID
    name: str
    url: str
    check_interval_seconds: int
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MonitoredServiceListResponse(BaseModel):
    """Paginated list of registered services."""

    services: list[MonitoredServiceResponse]
    total: int


class CheckResultResponse(BaseModel):
    """A single health-check result."""

    id: uuid.UUID
    service_id: uuid.UUID
    checked_at: datetime
    status: str = Field(description="One of: healthy, degraded, down.")
    status_code: int | None = None
    response_time_ms: float | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class CheckHistoryResponse(BaseModel):
    """Recent check results for a service."""

    service_id: uuid.UUID
    checks: list[CheckResultResponse]


class UptimeResponse(BaseModel):
    """Uptime statistics for a monitored service over a rolling window."""

    service_id: uuid.UUID
    window_hours: int = Field(description="Rolling window size used for the calculation.")
    total_checks: int
    healthy_checks: int
    degraded_checks: int
    down_checks: int
    uptime_percentage: float = Field(description="Percentage of healthy checks (0 – 100).")
    avg_response_time_ms: float | None = Field(
        default=None,
        description="Average response time across healthy and degraded checks.",
    )


class IncidentResponse(BaseModel):
    """An open or resolved incident for a monitored service."""

    id: uuid.UUID
    service_id: uuid.UUID
    started_at: datetime
    resolved_at: datetime | None = None
    severity: str = Field(description="One of: warning, critical.")
    description: str

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    """List of incidents for a service."""

    service_id: uuid.UUID
    incidents: list[IncidentResponse]
