from src.main import healthcheck


def test_worker_healthcheck() -> None:
    assert healthcheck()["status"] == "ok"
