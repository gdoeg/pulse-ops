from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_liveness(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "PulseOps API"
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Process-Time"]


def test_readiness(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_metrics(client: TestClient) -> None:
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "pulseops_http_requests_total" in response.text
    assert response.headers["content-type"].startswith("text/plain")


def test_services_placeholder(client: TestClient) -> None:
    response = client.get("/services")

    assert response.status_code == 200
    payload = response.json()
    assert [service["name"] for service in payload["services"]] == [
        "postgres",
        "redis",
        "ai",
    ]
    assert payload["services"][2]["status"] == "ready"
