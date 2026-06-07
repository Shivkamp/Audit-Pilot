from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, status

from app.core.config import settings
from app.core.constants import STORAGE_BACKEND_LOCAL
from app.core.exceptions import AppException
from app.core.logging import logger
from app.storage.base import StorageBackend, StorageSaveResult
from app.utils.file_utils import get_upload_file_size, reset_upload_file_pointer


class LocalStorageBackend(StorageBackend):
    def __init__(self, upload_dir: str | None = None) -> None:
        self._upload_root = Path(upload_dir or settings.upload_dir)

    @property
    def backend_name(self) -> str:
        return STORAGE_BACKEND_LOCAL

    def save_upload_file(
        self,
        upload_file: UploadFile,
        workspace_id: UUID,
        document_id: UUID,
        stored_filename: str,
        max_size_bytes: int,
    ) -> StorageSaveResult:
        file_size_bytes = get_upload_file_size(upload_file)
        if file_size_bytes > max_size_bytes:
            raise AppException(
                message="File size exceeds the maximum allowed limit.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="DOCUMENT_FILE_TOO_LARGE",
            )

        relative_path = (
            Path("workspaces")
            / str(workspace_id)
            / "documents"
            / str(document_id)
            / stored_filename
        )
        destination_path = self._upload_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        bytes_written = 0
        reset_upload_file_pointer(upload_file)

        try:
            with destination_path.open("wb") as destination_file:
                while True:
                    chunk = upload_file.file.read(1024 * 1024)
                    if not chunk:
                        break

                    bytes_written += len(chunk)
                    if bytes_written > max_size_bytes:
                        raise AppException(
                            message="File size exceeds the maximum allowed limit.",
                            status_code=status.HTTP_400_BAD_REQUEST,
                            error_code="DOCUMENT_FILE_TOO_LARGE",
                        )

                    destination_file.write(chunk)

        except AppException:
            if destination_path.exists():
                destination_path.unlink(missing_ok=True)
            raise
        except OSError as exc:
            if destination_path.exists():
                destination_path.unlink(missing_ok=True)
            raise AppException(
                message="Failed to save document to local storage.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="LOCAL_STORAGE_SAVE_FAILED",
            ) from exc
        finally:
            reset_upload_file_pointer(upload_file)

        return StorageSaveResult(
            storage_backend=self.backend_name,
            storage_bucket=None,
            storage_key=relative_path.as_posix(),
            stored_filename=stored_filename,
            file_size_bytes=bytes_written,
        )

    def generate_download_url(self, storage_key: str, expiry_seconds: int) -> str:
        raise AppException(
            message="Presigned download URLs are only supported for S3-backed documents for now.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PRESIGNED_URL_NOT_SUPPORTED",
        )

    def delete_file(self, storage_key: str) -> None:
        try:
            upload_root = self._upload_root.resolve()
            file_path = (self._upload_root / Path(storage_key)).resolve()

            # Guard: ensure the resolved path stays inside the upload root.
            if not str(file_path).startswith(str(upload_root) + "/") and file_path != upload_root:
                logger.warning(
                    "Refusing to delete file outside upload root for storage_key=%s",
                    storage_key,
                )
                return

            if file_path.exists():
                file_path.unlink()
        except OSError:
            logger.warning(
                "Failed to clean up local file after metadata save failure: %s",
                storage_key,
                exc_info=True,
            )
