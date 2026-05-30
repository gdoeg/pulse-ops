"""FastAPI entrypoint for PulseOps backend services."""

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(title="PulseOps API")
app.include_router(health_router)
