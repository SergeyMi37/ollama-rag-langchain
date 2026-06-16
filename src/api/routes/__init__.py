"""API роуты."""

from src.api.routes.frontend import router as frontend_router
from src.api.routes.health import router as health_router
from src.api.routes.query import router as query_router

__all__ = ["frontend_router", "health_router", "query_router"]
