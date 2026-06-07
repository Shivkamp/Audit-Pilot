from __future__ import annotations

from pathlib import Path
from uuid import UUID

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile, status

from app.core.config import settings
from app.core.constants import STORAGE_BACKEND_S3
from app.core.exceptions import AppException
from app.core.logging import logger
from app.storage.base import StorageBackend, StorageSaveResult
from app.utils.file_utils import get_upload_file_size, reset_upload_file_pointer


class S3StorageBackend(StorageBackend):
    def __init__(self) -> None:
        if not settings.aws_s3_bucket:
            raise AppException(
                message="AWS_S3_BUCKET is required when STORAGE_BACKEND is set to s3.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="S3_BUCKET_NOT_CONFIGURED",
            )

        if not settings.aws_region:
            raise AppException(
                message="AWS_REGION is required when STORAGE_BACKEND is set to s3.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="S3_REGION_NOT_CONFIGURED",
            )

        client_kwargs: dict[str, str] = {"region_name": settings.aws_region}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self._bucket = settings.aws_s3_bucket
        self._client = boto3.client("s3", **client_kwargs)

    @property
    def backend_name(self) -> str:
        return STORAGE_BACKEND_S3

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

        storage_key = (
            f"workspaces/{workspace_id}/documents/{document_id}/{stored_filename}"
        )

        extra_args: dict[str, str] = {}
        if upload_file.content_type:
            extra_args["ContentType"] = upload_file.content_type

        reset_upload_file_pointer(upload_file)
        try:
            self._client.upload_fileobj(
                upload_file.file,
                self._bucket,
                storage_key,
                ExtraArgs=extra_args if extra_args else None,
            )
        except (ClientError, BotoCoreError) as exc:
            raise AppException(
                message="Failed to upload document to S3 storage.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="S3_UPLOAD_FAILED",
            ) from exc
        # finally:
        #     reset_upload_file_pointer(upload_file)

        return StorageSaveResult(
            storage_backend=self.backend_name,
            storage_bucket=self._bucket,
            storage_key=storage_key,
            stored_filename=stored_filename,
            file_size_bytes=file_size_bytes,
        )

    def generate_download_url(self, storage_key: str, expiry_seconds: int) -> str:
        try:
            return self._client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self._bucket, "Key": storage_key},
                ExpiresIn=expiry_seconds,
            )
        except (ClientError, BotoCoreError) as exc:
            raise AppException(
                message="Failed to generate presigned download URL.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="S3_PRESIGNED_URL_FAILED",
            ) from exc

    def download_to_file(self, storage_key: str, dest_path: Path) -> None:
        try:
            self._client.download_file(self._bucket, storage_key, str(dest_path))
        except (ClientError, BotoCoreError) as exc:
            raise AppException(
                message="Failed to download document from S3 for processing.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="S3_DOWNLOAD_FAILED",
            ) from exc

    def delete_file(self, storage_key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=storage_key)
        except (ClientError, BotoCoreError):
            logger.warning(
                "Failed to clean up S3 object after metadata save failure: %s",
                storage_key,
                exc_info=True,
            )
