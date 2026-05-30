"""Domain-level application exceptions."""


class PulseOpsError(Exception):
    """Base application error translated into an API response."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "pulseops_error",
        status_code: int = 400,
        details: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
