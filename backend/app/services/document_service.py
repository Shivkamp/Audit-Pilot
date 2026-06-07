from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    DOCUMENT_STATUS_DELETED,
    DOCUMENT_STATUS_UPLOADED,
    DOCUMENT_TYPE_UNKNOWN,
    DOCUMENT_UPLOAD_SOURCE_MANUAL,
    STORAGE_BACKEND_S3,
)
from app.core.exceptions import AppException
from app.core.logging import logger
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentDownloadUrlResponse
from app.services.processing_job_service import ProcessingJobService
from app.services.workspace_service import WorkspaceService
from app.storage.base import StorageBackend
from app.storage.service import StorageService
from app.utils.file_utils import (
    generate_safe_filename,
    sanitize_filename,
    validate_file_extension,
)


class DocumentService:
    @staticmethod
    def upload_document(
        db: Session,
        workspace_id: UUID,
        file: UploadFile,
    ) -> tuple[Document, ProcessingJob]:
        WorkspaceService.get_workspace(db, workspace_id)

        original_filename = sanitize_filename(file.filename or "")
        file_extension = validate_file_extension(original_filename)
        stored_filename = generate_safe_filename(original_filename)

        document_id = uuid4()
        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        storage_backend = StorageService.get_backend()

        storage_result = storage_backend.save_upload_file(
            upload_file=file,
            workspace_id=workspace_id,
            document_id=document_id,
            stored_filename=stored_filename,
            max_size_bytes=max_size_bytes,
        )

        document_payload = DocumentCreate(
            id=document_id,
            workspace_id=workspace_id,
            original_filename=original_filename,
            stored_filename=storage_result.stored_filename,
            file_extension=file_extension,
            content_type=file.content_type,
            file_size_bytes=storage_result.file_size_bytes,
            storage_backend=storage_result.storage_backend,
            storage_bucket=storage_result.storage_bucket,
            storage_key=storage_result.storage_key,
            document_type=DOCUMENT_TYPE_UNKNOWN,
            status=DOCUMENT_STATUS_UPLOADED,
            upload_source=DOCUMENT_UPLOAD_SOURCE_MANUAL,
        )

        try:
            document = DocumentRepository.create(db, document_payload)
        except SQLAlchemyError as exc:
            db.rollback()
            DocumentService._attempt_storage_cleanup(
                backend=storage_backend,
                storage_key=storage_result.storage_key,
                document_id=document_id,
            )
            raise AppException(
                message="Document upload failed while saving metadata.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="DOCUMENT_METADATA_SAVE_FAILED",
            ) from exc

        processing_job = ProcessingJobService.create_document_processing_job(db, document)
        return document, processing_job

    @staticmethod
    def list_workspace_documents(db: Session, workspace_id: UUID) -> list[Document]:
        WorkspaceService.get_workspace(db, workspace_id)
        return DocumentRepository.list_by_workspace_id(db, workspace_id, include_deleted=False)

    @staticmethod
    def get_document(db: Session, document_id: UUID) -> Document:
        document = DocumentRepository.get_by_id(db, document_id)
        if document is None or document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="DOCUMENT_NOT_FOUND",
            )
        return document

    @staticmethod
    def delete_document(db: Session, document_id: UUID) -> Document:
        document = DocumentRepository.get_by_id(db, document_id)
        if document is None:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="DOCUMENT_NOT_FOUND",
            )

        if document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Document is already deleted.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="DOCUMENT_ALREADY_DELETED",
            )

        return DocumentRepository.update_status(db, document, DOCUMENT_STATUS_DELETED)

    @staticmethod
    def generate_download_url(db: Session, document_id: UUID) -> DocumentDownloadUrlResponse:
        document = DocumentService.get_document(db, document_id)
        if document.storage_backend != STORAGE_BACKEND_S3:
            raise AppException(
                message="Presigned download URLs are only supported for S3-backed documents for now.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="PRESIGNED_URL_NOT_SUPPORTED",
            )

        storage_backend = StorageService.get_backend(document.storage_backend)
        download_url = storage_backend.generate_download_url(
            document.storage_key,
            settings.aws_presigned_url_expiry_seconds,
        )

        return DocumentDownloadUrlResponse(
            document_id=document.id,
            download_url=download_url,
            expires_in_seconds=settings.aws_presigned_url_expiry_seconds,
        )

    @staticmethod
    def _attempt_storage_cleanup(
        backend: StorageBackend,
        storage_key: str,
        document_id: UUID,
    ) -> None:
        try:
            backend.delete_file(storage_key)
            logger.info(
                "Cleaned up storage artifact for document_id=%s storage_key=%s",
                document_id,
                storage_key,
            )
        except Exception:  # pragma: no cover - best effort cleanup
            logger.warning(
                "Document metadata save failed for document_id=%s; "
                "storage artifact may remain at %s",
                document_id,
                storage_key,
                exc_info=True,
            )
