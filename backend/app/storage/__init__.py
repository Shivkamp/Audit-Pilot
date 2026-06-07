"""Storage backend abstractions for document persistence."""

from app.storage.base import StorageBackend, StorageSaveResult
from app.storage.service import StorageService

__all__ = ["StorageBackend", "StorageSaveResult", "StorageService"]
