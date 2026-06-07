from __future__ import annotations

from fastapi import status

from app.core.config import settings
from app.core.constants import STORAGE_BACKEND_LOCAL, STORAGE_BACKEND_S3
from app.core.exceptions import AppException
from app.storage.base import StorageBackend
from app.storage.local import LocalStorageBackend
from app.storage.s3 import S3StorageBackend


class StorageService:
    @staticmethod
    def get_backend(storage_backend: str | None = None) -> StorageBackend:
        backend_name = (storage_backend or settings.storage_backend).strip().lower()

        if backend_name == STORAGE_BACKEND_LOCAL:
            return LocalStorageBackend(settings.upload_dir)
        if backend_name == STORAGE_BACKEND_S3:
            return S3StorageBackend()

        raise AppException(
            message=f"Invalid storage backend configured: {backend_name}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INVALID_STORAGE_BACKEND",
        )
