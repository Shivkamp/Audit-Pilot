from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from fastapi import UploadFile


@dataclass(slots=True)
class StorageSaveResult:
    storage_backend: str
    storage_bucket: str | None
    storage_key: str
    stored_filename: str
    file_size_bytes: int


class StorageBackend(ABC):
    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Return the backend identifier (for example: local, s3)."""

    @abstractmethod
    def save_upload_file(
        self,
        upload_file: UploadFile,
        workspace_id: UUID,
        document_id: UUID,
        stored_filename: str,
        max_size_bytes: int,
    ) -> StorageSaveResult:
        """Persist an uploaded file and return metadata about where/how it was stored."""

    @abstractmethod
    def generate_download_url(self, storage_key: str, expiry_seconds: int) -> str:
        """Return a temporary URL for downloading the object from this backend."""

    def delete_file(self, storage_key: str) -> None:
        """Best-effort cleanup called when DB metadata save fails after storage write.

        Subclasses **must** override this with real cleanup logic.  The base
        implementation is a no-op; leaving it un-overridden means orphaned
        storage artifacts will not be removed on rollback.
        """
