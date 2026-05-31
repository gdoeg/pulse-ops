"""Async monitoring worker – polls services, measures latency, stores results."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import WorkerSettings
from src.database import WorkerDatabase
from src.logging import get_logger
from src.models import CheckResult, Incident, MonitoredService
from src.queue import CheckTask, TaskQueue, make_task

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Health-check classification helpers
# ---------------------------------------------------------------------------


def classify_status(
    *,
    status_code: int | None,
    response_time_ms: float | None,
    error: str | None,
    degraded_threshold_ms: float,
) -> str:
    """Determine check status from raw HTTP outcome."""
    if error is not None or status_code is None:
        return "down"
    if status_code >= 500:
        return "down"
    if response_time_ms is not None and response_time_ms > degraded_threshold_ms:
        return "degraded"
    if status_code >= 300:
        return "degraded"
    return "healthy"


# ---------------------------------------------------------------------------
# HTTP health-check with retry / exponential backoff
# ---------------------------------------------------------------------------


async def perform_check(
    url: str,
    *,
    http_timeout: float,
    max_retries: int,
    degraded_threshold_ms: float,
) -> dict[str, Any]:
    """
    Execute an HTTP GET health check against *url*.

    Retries up to *max_retries* times on network errors using exponential
    backoff (1 s, 2 s, 4 s, …).  Returns a dict suitable for persisting as a
    CheckResult row.
    """
    attempt = 0
    last_error: str | None = None

    async with httpx.AsyncClient(timeout=http_timeout, follow_redirects=True) as client:
        while attempt <= max_retries:
            attempt += 1
            status_code: int | None = None
            response_time_ms: float | None = None
            error: str | None = None

            try:
                start = asyncio.get_event_loop().time()
                response = await client.get(url)
                elapsed = asyncio.get_event_loop().time() - start
                status_code = response.status_code
                response_time_ms = round(elapsed * 1000, 3)
            except httpx.TimeoutException as exc:
                error = f"timeout: {exc}"
            except httpx.RequestError as exc:
                error = f"request_error: {exc}"

            status = classify_status(
                status_code=status_code,
                response_time_ms=response_time_ms,
                error=error,
                degraded_threshold_ms=degraded_threshold_ms,
            )

            logger.info(
                "health check result",
                extra={
                    "url": url,
                    "status": status,
                    "status_code": status_code,
                    "response_time_ms": response_time_ms,
                    "attempt": attempt,
                    "error": error,
                },
            )

            # Healthy / degraded results don't need retry.
            if status != "down":
                return {
                    "status": status,
                    "status_code": status_code,
                    "response_time_ms": response_time_ms,
                    "error_message": None,
                }

            last_error = error or (f"HTTP {status_code}" if status_code else "unknown")

            if attempt <= max_retries:
                backoff = 2 ** (attempt - 1)
                logger.warning(
                    "check failed, retrying",
                    extra={
                        "url": url,
                        "attempt": attempt,
                        "backoff_seconds": backoff,
                        "error": last_error,
                    },
                )
                await asyncio.sleep(backoff)

    return {
        "status": "down",
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "error_message": last_error,
    }


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


async def _persist_check_result(
    session: AsyncSession,
    service_id: uuid.UUID,
    result: dict[str, Any],
) -> None:
    """Write a CheckResult row and update incident state."""
    check = CheckResult(
        service_id=service_id,
        status=result["status"],
        status_code=result.get("status_code"),
        response_time_ms=result.get("response_time_ms"),
        error_message=result.get("error_message"),
    )
    session.add(check)
    await session.flush()

    await _update_incident_state(session, service_id, result["status"])
    await session.commit()


async def _update_incident_state(
    session: AsyncSession,
    service_id: uuid.UUID,
    status: str,
) -> None:
    """Open a new incident or resolve the current open one."""
    open_result = await session.execute(
        select(Incident).where(
            Incident.service_id == service_id,
            Incident.resolved_at.is_(None),
        )
    )
    open_incident = open_result.scalar_one_or_none()

    if status == "healthy":
        if open_incident is not None:
            await session.execute(
                update(Incident)
                .where(Incident.id == open_incident.id)
                .values(resolved_at=datetime.now(UTC))
            )
        return

    if open_incident is not None:
        return  # already tracking this incident

    recent_rows = await session.execute(
        select(CheckResult)
        .where(CheckResult.service_id == service_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(5)
    )
    recent = recent_rows.scalars().all()
    consecutive_failures = sum(1 for c in recent if c.status != "healthy")

    if consecutive_failures >= 2:
        severity = "critical" if status == "down" else "warning"
        description = (
            f"Service entered '{status}' state after "
            f"{consecutive_failures} consecutive failed checks."
        )
        session.add(Incident(service_id=service_id, severity=severity, description=description))


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------


class MonitorWorker:
    """
    Async polling worker for PulseOps service monitoring.

    Architecture
    ------------
    * A *scheduler* coroutine wakes up every ``scheduler_interval_seconds``
      and enqueues health-check tasks for every enabled service whose next
      check window has elapsed.
    * A pool of *consumer* coroutines drains the Redis queue concurrently,
      executing HTTP checks and persisting results to PostgreSQL.
    * Service poll-timestamps are tracked in an in-process dict to avoid
      a dedicated ``last_checked`` DB column.
    """

    def __init__(
        self,
        settings: WorkerSettings,
        database: WorkerDatabase,
        queue: TaskQueue,
    ) -> None:
        self._settings = settings
        self._db = database
        self._queue = queue
        # service_id -> last scheduled timestamp
        self._last_scheduled: dict[str, datetime] = {}
        self._shutdown_event = asyncio.Event()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> None:
        """Start the scheduler and consumer pool and block until shutdown."""
        logger.info("monitor worker starting")
        tasks = [
            asyncio.create_task(self._scheduler_loop()),
            *[
                asyncio.create_task(self._consumer_loop(worker_id=i))
                for i in range(self._settings.worker_concurrency)
            ],
        ]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            logger.info("monitor worker stopped")

    def request_shutdown(self) -> None:
        """Signal the worker to stop after the current cycle."""
        self._shutdown_event.set()

    # ------------------------------------------------------------------
    # Scheduler
    # ------------------------------------------------------------------

    async def _scheduler_loop(self) -> None:
        """Periodically enqueue check tasks for services that are due."""
        while not self._shutdown_event.is_set():
            try:
                await self._schedule_due_checks()
            except Exception:
                logger.exception("scheduler loop error")

            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self._settings.scheduler_interval_seconds,
                )
            except TimeoutError:
                pass

    async def _schedule_due_checks(self) -> None:
        """Load enabled services and enqueue those whose interval has elapsed."""
        async with self._db.session() as session:
            result = await session.execute(
                select(MonitoredService).where(MonitoredService.enabled.is_(True))
            )
            services = result.scalars().all()

        now = datetime.now(UTC)
        enqueued = 0
        for svc in services:
            sid = str(svc.id)
            last = self._last_scheduled.get(sid)
            interval = svc.check_interval_seconds
            if last is None or (now - last).total_seconds() >= interval:
                task = make_task(sid, svc.name, svc.url)
                await self._queue.push(task)
                self._last_scheduled[sid] = now
                enqueued += 1

        if enqueued:
            logger.info(
                "scheduled check tasks",
                extra={"service_name": f"{enqueued} services"},
            )

    # ------------------------------------------------------------------
    # Consumer
    # ------------------------------------------------------------------

    async def _consumer_loop(self, *, worker_id: int) -> None:
        """Drain the Redis queue and execute health checks."""
        logger.info("consumer started", extra={"service_name": f"worker-{worker_id}"})
        while not self._shutdown_event.is_set():
            try:
                task = await self._queue.pop(timeout=1.0)
                if task is None:
                    continue
                await self._process_task(task)
            except Exception:
                logger.exception(
                    "consumer loop error",
                    extra={"service_name": f"worker-{worker_id}"},
                )

    async def _process_task(self, task: CheckTask) -> None:
        """Execute a single health-check task and persist the outcome."""
        logger.info(
            "checking service",
            extra={"service_id": task.service_id, "service_name": task.name, "url": task.url},
        )
        result = await perform_check(
            task.url,
            http_timeout=self._settings.http_timeout_seconds,
            max_retries=self._settings.max_retries,
            degraded_threshold_ms=self._settings.degraded_threshold_ms,
        )
        service_id = uuid.UUID(task.service_id)
        async with self._db.session() as session:
            await _persist_check_result(session, service_id, result)

        logger.info(
            "check persisted",
            extra={
                "service_id": task.service_id,
                "service_name": task.name,
                "status": result["status"],
                "response_time_ms": result.get("response_time_ms"),
            },
        )
