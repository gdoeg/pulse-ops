"""Worker process entrypoint for PulseOps background workloads."""


def healthcheck() -> dict[str, str]:
    """Placeholder healthcheck used by worker supervisors."""
    return {"status": "ok"}


if __name__ == "__main__":
    print("PulseOps workers started")
