"""Tests for the /monitor service monitoring API endpoints."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.monitor import (
    CheckHistoryResponse,
    CheckResultResponse,
    IncidentListResponse,
    IncidentResponse,
    MonitoredServiceListResponse,
    MonitoredServiceResponse,
    UptimeResponse,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SERVICE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
NOW = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

SAMPLE_SERVICE = MonitoredServiceResponse(
    id=SERVICE_ID,
    name="example-api",
    url="https://example.com/health",
    check_interval_seconds=60,
    enabled=True,
    created_at=NOW,
    updated_at=NOW,
)

SAMPLE_CHECK = CheckResultResponse(
    id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
    service_id=SERVICE_ID,
    checked_at=NOW,
    status="healthy",
    status_code=200,
    response_time_ms=42.5,
    error_message=None,
)

SAMPLE_UPTIME = UptimeResponse(
    service_id=SERVICE_ID,
    window_hours=24,
    total_checks=100,
    healthy_checks=98,
    degraded_checks=1,
    down_checks=1,
    uptime_percentage=98.0,
    avg_response_time_ms=55.2,
)

SAMPLE_INCIDENT = IncidentResponse(
    id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
    service_id=SERVICE_ID,
    started_at=NOW,
    resolved_at=None,
    severity="critical",
    description="Service entered 'down' state after 2 consecutive failed checks.",
)


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def _apply_overrides(mock_monitor_service: Any | None = None) -> None:
    """
    Always override get_db_session (so tests never touch a real DB) and
    optionally override get_monitor_service with a provided mock.
    """
    from app.core.dependencies import get_db_session, get_monitor_service

    async def fake_db_session() -> AsyncIterator[AsyncMock]:
        yield AsyncMock()

    app.dependency_overrides[get_db_session] = fake_db_session

    if mock_monitor_service is not None:
        app.dependency_overrides[get_monitor_service] = lambda: mock_monitor_service


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests: POST /monitor/services
# ---------------------------------------------------------------------------


def test_register_service(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.register_service.return_value = SAMPLE_SERVICE
    _apply_overrides(mock_svc)
    try:
        response = client.post(
            "/monitor/services",
            json={
                "name": "example-api",
                "url": "https://example.com/health",
                "check_interval_seconds": 60,
                "enabled": True,
            },
        )
    finally:
        _clear_overrides()

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "example-api"
    assert payload["url"] == "https://example.com/health"
    assert payload["check_interval_seconds"] == 60
    assert payload["enabled"] is True


def test_register_service_invalid_url(client: TestClient) -> None:
    _apply_overrides()
    try:
        response = client.post(
            "/monitor/services",
            json={"name": "bad", "url": "not-a-url", "check_interval_seconds": 60},
        )
    finally:
        _clear_overrides()

    assert response.status_code == 422


def test_register_service_interval_too_short(client: TestClient) -> None:
    _apply_overrides()
    try:
        response = client.post(
            "/monitor/services",
            json={
                "name": "fast",
                "url": "https://example.com/health",
                "check_interval_seconds": 1,
            },
        )
    finally:
        _clear_overrides()

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests: GET /monitor/services
# ---------------------------------------------------------------------------


def test_list_services(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.list_monitored_services.return_value = MonitoredServiceListResponse(
        services=[SAMPLE_SERVICE],
        total=1,
    )
    _apply_overrides(mock_svc)
    try:
        response = client.get("/monitor/services")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["services"][0]["name"] == "example-api"


# ---------------------------------------------------------------------------
# Tests: GET /monitor/services/{id}
# ---------------------------------------------------------------------------


def test_get_service(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.get_service.return_value = SAMPLE_SERVICE
    _apply_overrides(mock_svc)
    try:
        response = client.get(f"/monitor/services/{SERVICE_ID}")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    assert response.json()["id"] == str(SERVICE_ID)


def test_get_service_not_found(client: TestClient) -> None:
    from app.core.exceptions import PulseOpsError

    mock_svc = AsyncMock()
    mock_svc.get_service.side_effect = PulseOpsError(
        "Service not found.", code="service_not_found", status_code=404
    )
    _apply_overrides(mock_svc)
    try:
        response = client.get(f"/monitor/services/{uuid.uuid4()}")
    finally:
        _clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests: GET /monitor/services/{id}/checks
# ---------------------------------------------------------------------------


def test_get_check_history(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.get_check_history.return_value = CheckHistoryResponse(
        service_id=SERVICE_ID,
        checks=[SAMPLE_CHECK],
    )
    _apply_overrides(mock_svc)
    try:
        response = client.get(f"/monitor/services/{SERVICE_ID}/checks")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["checks"]) == 1
    assert payload["checks"][0]["status"] == "healthy"
    assert payload["checks"][0]["response_time_ms"] == 42.5


# ---------------------------------------------------------------------------
# Tests: GET /monitor/services/{id}/uptime
# ---------------------------------------------------------------------------


def test_get_uptime(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.calculate_uptime.return_value = SAMPLE_UPTIME
    _apply_overrides(mock_svc)
    try:
        response = client.get(f"/monitor/services/{SERVICE_ID}/uptime?window_hours=24")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    payload = response.json()
    assert payload["uptime_percentage"] == 98.0
    assert payload["total_checks"] == 100
    assert payload["healthy_checks"] == 98
    assert payload["avg_response_time_ms"] == 55.2


def test_get_uptime_window_too_large(client: TestClient) -> None:
    _apply_overrides()
    try:
        response = client.get(f"/monitor/services/{SERVICE_ID}/uptime?window_hours=9999")
    finally:
        _clear_overrides()

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests: GET /monitor/services/{id}/incidents
# ---------------------------------------------------------------------------


def test_get_incidents(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.get_incidents.return_value = IncidentListResponse(
        service_id=SERVICE_ID,
        incidents=[SAMPLE_INCIDENT],
    )
    _apply_overrides(mock_svc)
    try:
        response = client.get(f"/monitor/services/{SERVICE_ID}/incidents")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["incidents"]) == 1
    assert payload["incidents"][0]["severity"] == "critical"
    assert payload["incidents"][0]["resolved_at"] is None


def test_get_incidents_open_only(client: TestClient) -> None:
    mock_svc = AsyncMock()
    mock_svc.get_incidents.return_value = IncidentListResponse(
        service_id=SERVICE_ID,
        incidents=[SAMPLE_INCIDENT],
    )
    _apply_overrides(mock_svc)
    try:
        response = client.get(f"/monitor/services/{SERVICE_ID}/incidents?open_only=true")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    mock_svc.get_incidents.assert_called_once()
    _, kwargs = mock_svc.get_incidents.call_args
    assert kwargs.get("open_only") is True
