"""Declarative SQLAlchemy base for future PulseOps persistence models."""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Common base class that future repository models will inherit from."""
