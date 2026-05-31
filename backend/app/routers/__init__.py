"""Aggregate API routers for the PulseOps backend."""

from fastapi import APIRouter

from app.routers.health import router as health_router
from app.routers.metrics import router as metrics_router
from app.routers.monitor import router as monitor_router
from app.routers.services import router as services_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(metrics_router)
api_router.include_router(monitor_router)
api_router.include_router(services_router)
