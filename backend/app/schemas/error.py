"""Error response schemas."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Consistent JSON payload for API errors."""

    code: str = Field(description="Machine-readable error code.")
    message: str = Field(description="Human-readable error message.")
    details: dict[str, str] = Field(
        default_factory=dict,
        description="Additional error detail fields.",
    )
    request_id: str | None = Field(
        default=None,
        description="Request correlation identifier for debugging.",
    )
