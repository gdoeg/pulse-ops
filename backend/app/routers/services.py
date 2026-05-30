"""Placeholder service inventory endpoints."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_service_catalog_service
from app.schemas.service import ServicesResponse
from app.services.service_catalog import ServiceCatalogService

router = APIRouter(tags=["services"])


@router.get(
    "/services",
    response_model=ServicesResponse,
    summary="List backend service placeholders",
)
async def list_services(
    service: ServiceCatalogService = Depends(get_service_catalog_service),
) -> ServicesResponse:
    """Return infrastructure services that the backend is prepared to use."""
    return service.list_services()
