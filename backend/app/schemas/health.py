"""Health and readiness response schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Structured health payload shared by liveness and readiness probes."""

    status: str = Field(description="Top-level application status.")
    service: str = Field(description="Service name reporting the health state.")
    environment: str = Field(description="Active deployment environment.")
    version: str = Field(description="API version string.")
