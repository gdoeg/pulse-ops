"""Tests for the PulseOps monitoring worker logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.monitor import MonitorWorker, classify_status, perform_check
from src.queue import CheckTask, TaskQueue, make_task

# ---------------------------------------------------------------------------
# classify_status
# ---------------------------------------------------------------------------


def test_classify_healthy() -> None:
    assert (
        classify_status(
            status_code=200,
            response_time_ms=100.0,
            error=None,
            degraded_threshold_ms=5000.0,
        )
        == "healthy"
    )


def test_classify_degraded_slow_response() -> None:
    assert (
        classify_status(
            status_code=200,
            response_time_ms=6000.0,
            error=None,
            degraded_threshold_ms=5000.0,
        )
        == "degraded"
    )


def test_classify_degraded_4xx() -> None:
    assert (
        classify_status(
            status_code=404,
            response_time_ms=50.0,
            error=None,
            degraded_threshold_ms=5000.0,
        )
        == "degraded"
    )


def test_classify_down_5xx() -> None:
    assert (
        classify_status(
            status_code=503,
            response_time_ms=50.0,
            error=None,
            degraded_threshold_ms=5000.0,
        )
        == "down"
    )


def test_classify_down_network_error() -> None:
    assert (
        classify_status(
            status_code=None,
            response_time_ms=None,
            error="connection refused",
            degraded_threshold_ms=5000.0,
        )
        == "down"
    )


def test_classify_down_no_status_code() -> None:
    assert (
        classify_status(
            status_code=None,
            response_time_ms=None,
            error=None,
            degraded_threshold_ms=5000.0,
        )
        == "down"
    )


# ---------------------------------------------------------------------------
# perform_check – success path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_perform_check_healthy() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("src.monitor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.time.side_effect = [0.0, 0.1]  # 100 ms
            result = await perform_check(
                "https://example.com/health",
                http_timeout=10.0,
                max_retries=3,
                degraded_threshold_ms=5000.0,
            )

    assert result["status"] == "healthy"
    assert result["status_code"] == 200
    assert result["error_message"] is None


@pytest.mark.asyncio
async def test_perform_check_down_exhausts_retries() -> None:
    import httpx as _httpx

    with patch("src.monitor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.side_effect = _httpx.RequestError("connection refused")
        mock_client_cls.return_value = mock_client

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await perform_check(
                "https://example.com/health",
                http_timeout=10.0,
                max_retries=2,
                degraded_threshold_ms=5000.0,
            )

    assert result["status"] == "down"
    assert result["error_message"] is not None
    assert "request_error" in result["error_message"]


# ---------------------------------------------------------------------------
# make_task / CheckTask round-trip
# ---------------------------------------------------------------------------


def test_make_task_round_trip() -> None:
    sid = str(uuid.uuid4())
    task = make_task(sid, "my-api", "https://my-api.example.com/health")
    assert task.service_id == sid
    assert task.name == "my-api"
    assert task.url == "https://my-api.example.com/health"

    restored = CheckTask.from_dict(task.to_dict())
    assert restored.service_id == task.service_id
    assert restored.name == task.name
    assert restored.url == task.url
    assert restored.enqueued_at == task.enqueued_at


# ---------------------------------------------------------------------------
# MonitorWorker._schedule_due_checks
# ---------------------------------------------------------------------------


def _make_db_mock(mock_session: AsyncMock) -> MagicMock:
    """Build a MagicMock for WorkerDatabase whose .session() is a proper async CM."""
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    mock_db = MagicMock()
    mock_db.session.return_value = mock_cm
    return mock_db


@pytest.fixture
def worker_settings():
    from src.config import WorkerSettings

    return WorkerSettings(
        environment="test",
        postgres_host="localhost",
        scheduler_interval_seconds=5.0,
        worker_concurrency=1,
        max_retries=0,
        http_timeout_seconds=5.0,
        degraded_threshold_ms=5000.0,
    )


@pytest.mark.asyncio
async def test_schedule_due_checks_enqueues_enabled_services(worker_settings) -> None:
    sid = uuid.uuid4()
    mock_service = MagicMock()
    mock_service.id = sid
    mock_service.name = "test-api"
    mock_service.url = "https://test-api.example.com/health"
    mock_service.enabled = True
    mock_service.check_interval_seconds = 60

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_service]
    mock_session.execute.return_value = mock_result

    mock_db = _make_db_mock(mock_session)
    mock_queue = AsyncMock(spec=TaskQueue)

    worker = MonitorWorker(worker_settings, mock_db, mock_queue)
    await worker._schedule_due_checks()

    mock_queue.push.assert_called_once()
    pushed_task = mock_queue.push.call_args[0][0]
    assert pushed_task.service_id == str(sid)
    assert pushed_task.name == "test-api"


@pytest.mark.asyncio
async def test_schedule_due_checks_skips_recently_scheduled(worker_settings) -> None:
    sid = uuid.uuid4()
    mock_service = MagicMock()
    mock_service.id = sid
    mock_service.name = "test-api"
    mock_service.url = "https://test-api.example.com/health"
    mock_service.enabled = True
    mock_service.check_interval_seconds = 3600  # not due for another hour

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_service]
    mock_session.execute.return_value = mock_result

    mock_db = _make_db_mock(mock_session)
    mock_queue = AsyncMock(spec=TaskQueue)

    worker = MonitorWorker(worker_settings, mock_db, mock_queue)
    # Simulate that the service was just checked.
    worker._last_scheduled[str(sid)] = datetime.now(UTC)

    await worker._schedule_due_checks()

    mock_queue.push.assert_not_called()


# ---------------------------------------------------------------------------
# healthcheck (smoke test)
# ---------------------------------------------------------------------------


def test_worker_healthcheck() -> None:
    from src.main import healthcheck

    assert healthcheck()["status"] == "ok"
