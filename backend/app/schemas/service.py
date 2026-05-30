"""Service catalog response schemas."""

from pydantic import BaseModel, Field


class ServiceDescriptor(BaseModel):
    """Describe an infrastructure dependency or platform integration."""

    name: str = Field(description="Service identifier.")
    kind: str = Field(description="Infrastructure category.")
    status: str = Field(description="Current configuration state.")
    detail: str = Field(description="Operational placeholder detail.")


class ServicesResponse(BaseModel):
    """List of backend infrastructure services available to PulseOps."""

    services: list[ServiceDescriptor]
