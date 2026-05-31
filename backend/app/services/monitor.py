"""Business logic for the service monitoring engine."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PulseOpsError
from app.models.check_result import CheckResult
from app.models.incident import Incident
from app.models.monitored_service import MonitoredService
from app.schemas.monitor import (
    CheckHistoryResponse,
    CheckResultResponse,
    IncidentListResponse,
    IncidentResponse,
    MonitoredServiceCreate,
    MonitoredServiceListResponse,
    MonitoredServiceResponse,
    UptimeResponse,
)

_DEGRADED_THRESHOLD_MS = 5_000.0  # 5 s


class MonitorService:
    """Manage service registration, check persistence, and uptime analytics."""

    # ------------------------------------------------------------------
    # Service registration
    # ------------------------------------------------------------------

    async def register_service(
        self,
        session: AsyncSession,
        data: MonitoredServiceCreate,
    ) -> MonitoredServiceResponse:
        """Persist a new monitored service and return its full representation."""
        service = MonitoredService(
            name=data.name,
            url=str(data.url),
            check_interval_seconds=data.check_interval_seconds,
            enabled=data.enabled,
        )
        session.add(service)
        await session.commit()
        await session.refresh(service)
        return MonitoredServiceResponse.model_validate(service)

    async def list_monitored_services(
        self,
        session: AsyncSession,
    ) -> MonitoredServiceListResponse:
        """Return all registered services."""
        result = await session.execute(
            select(MonitoredService).order_by(MonitoredService.created_at.desc())
        )
        services = result.scalars().all()
        return MonitoredServiceListResponse(
            services=[MonitoredServiceResponse.model_validate(s) for s in services],
            total=len(services),
        )

    async def get_service(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
    ) -> MonitoredServiceResponse:
        """Fetch a single service by ID, raising 404 if missing."""
        service = await self._require_service(session, service_id)
        return MonitoredServiceResponse.model_validate(service)

    # ------------------------------------------------------------------
    # Check result persistence
    # ------------------------------------------------------------------

    async def record_check_result(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
        *,
        status: str,
        status_code: int | None = None,
        response_time_ms: float | None = None,
        error_message: str | None = None,
    ) -> CheckResultResponse:
        """Persist a health-check result and update incident state."""
        result = CheckResult(
            service_id=service_id,
            status=status,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )
        session.add(result)
        await session.flush()  # populate id / checked_at before incident logic

        await self._update_incident_state(session, service_id, status)
        await session.commit()
        await session.refresh(result)
        return CheckResultResponse.model_validate(result)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_check_history(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
        limit: int = 100,
    ) -> CheckHistoryResponse:
        """Return the most recent check results for a service."""
        await self._require_service(session, service_id)
        result = await session.execute(
            select(CheckResult)
            .where(CheckResult.service_id == service_id)
            .order_by(CheckResult.checked_at.desc())
            .limit(limit)
        )
        checks = result.scalars().all()
        return CheckHistoryResponse(
            service_id=service_id,
            checks=[CheckResultResponse.model_validate(c) for c in checks],
        )

    async def calculate_uptime(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
        window_hours: int = 24,
    ) -> UptimeResponse:
        """Calculate uptime statistics over a rolling time window."""
        await self._require_service(session, service_id)
        since = datetime.now(UTC) - timedelta(hours=window_hours)

        rows = await session.execute(
            select(CheckResult)
            .where(
                CheckResult.service_id == service_id,
                CheckResult.checked_at >= since,
            )
            .order_by(CheckResult.checked_at.desc())
        )
        checks = rows.scalars().all()

        total = len(checks)
        healthy = sum(1 for c in checks if c.status == "healthy")
        degraded = sum(1 for c in checks if c.status == "degraded")
        down = sum(1 for c in checks if c.status == "down")

        uptime_pct = (healthy / total * 100.0) if total else 0.0

        response_times = [
            c.response_time_ms
            for c in checks
            if c.response_time_ms is not None and c.status in ("healthy", "degraded")
        ]
        avg_ms = sum(response_times) / len(response_times) if response_times else None

        return UptimeResponse(
            service_id=service_id,
            window_hours=window_hours,
            total_checks=total,
            healthy_checks=healthy,
            degraded_checks=degraded,
            down_checks=down,
            uptime_percentage=round(uptime_pct, 4),
            avg_response_time_ms=round(avg_ms, 3) if avg_ms is not None else None,
        )

    # ------------------------------------------------------------------
    # Incidents
    # ------------------------------------------------------------------

    async def get_incidents(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
        *,
        open_only: bool = False,
    ) -> IncidentListResponse:
        """Return incidents for a service, optionally filtered to open ones."""
        await self._require_service(session, service_id)
        query = select(Incident).where(Incident.service_id == service_id)
        if open_only:
            query = query.where(Incident.resolved_at.is_(None))
        query = query.order_by(Incident.started_at.desc())

        result = await session.execute(query)
        incidents = result.scalars().all()
        return IncidentListResponse(
            service_id=service_id,
            incidents=[IncidentResponse.model_validate(i) for i in incidents],
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _require_service(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
    ) -> MonitoredService:
        """Return the service or raise a 404 PulseOpsError."""
        result = await session.execute(
            select(MonitoredService).where(MonitoredService.id == service_id)
        )
        service = result.scalar_one_or_none()
        if service is None:
            raise PulseOpsError(
                f"Service {service_id} not found.",
                code="service_not_found",
                status_code=404,
            )
        return service

    async def _update_incident_state(
        self,
        session: AsyncSession,
        service_id: uuid.UUID,
        status: str,
    ) -> None:
        """Open a new incident or resolve the current open one based on check status."""
        open_incident_result = await session.execute(
            select(Incident).where(
                Incident.service_id == service_id,
                Incident.resolved_at.is_(None),
            )
        )
        open_incident = open_incident_result.scalar_one_or_none()

        if status == "healthy":
            if open_incident is not None:
                await session.execute(
                    update(Incident)
                    .where(Incident.id == open_incident.id)
                    .values(resolved_at=datetime.now(UTC))
                )
            return

        if open_incident is not None:
            # Incident already open – no further action needed.
            return

        # Count recent consecutive non-healthy checks to determine severity.
        recent_result = await session.execute(
            select(CheckResult)
            .where(CheckResult.service_id == service_id)
            .order_by(CheckResult.checked_at.desc())
            .limit(5)
        )
        recent = recent_result.scalars().all()
        consecutive_failures = 0
        for check in recent:
            if check.status != "healthy":
                consecutive_failures += 1
            else:
                break

        # Open an incident after 2+ consecutive non-healthy checks.
        if consecutive_failures >= 2:
            severity = "critical" if status == "down" else "warning"
            description = (
                f"Service entered '{status}' state after "
                f"{consecutive_failures} consecutive failed checks."
            )
            session.add(
                Incident(
                    service_id=service_id,
                    severity=severity,
                    description=description,
                )
            )
