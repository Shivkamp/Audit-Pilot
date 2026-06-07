"""Top-level API router module (re-exports v1 router)."""

from app.api.v1.router import api_router

__all__ = ["api_router"]
