from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.constants import (
    DOCUMENT_STATUS_DELETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_TYPE_DOCUMENT_PROCESSING,
)
from app.core.exceptions import AppException
from app.core.logging import logger
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.repositories.document_repository import DocumentRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.workspace_repository import WorkspaceRepository


class ProcessingJobService:
    @staticmethod
    def create_document_processing_job(db: Session, document: Document) -> ProcessingJob:
        if document is None:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="DOCUMENT_NOT_FOUND",
            )

        if document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Cannot create processing job for deleted document.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="DOCUMENT_DELETED",
            )

        workspace = WorkspaceRepository.get_by_id(db, document.workspace_id)
        if workspace is None:
            raise AppException(
                message="Workspace not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="WORKSPACE_NOT_FOUND",
            )

        job = ProcessingJobRepository.create(
            db,
            {
                "document_id": document.id,
                "workspace_id": document.workspace_id,
                "job_type": JOB_TYPE_DOCUMENT_PROCESSING,
                "status": JOB_STATUS_PENDING,
                "progress_percent": 0,
                "current_step": "Awaiting document processing",
            },
        )

        try:
            from app.tasks.document_tasks import process_document_task

            async_result = process_document_task.delay(str(job.id))
            return ProcessingJobRepository.set_celery_task_id(db, job, async_result.id)
        except Exception:
            logger.exception("Failed to enqueue Celery task for job_id=%s", job.id)
            try:
                db.rollback()
                ProcessingJobRepository.update_status(
                    db,
                    job,
                    status=JOB_STATUS_FAILED,
                    current_step="Failed to enqueue document processing task",
                    error_message="Unable to enqueue processing task.",
                )
            except Exception:
                logger.exception(
                    "Failed to mark job as failed after enqueue error, job_id=%s", job.id
                )
            raise AppException(
                message="Document processing job enqueue failed.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="JOB_ENQUEUE_FAILED",
            )

    @staticmethod
    def get_job(db: Session, job_id: UUID) -> ProcessingJob:
        job = ProcessingJobRepository.get_by_id(db, job_id)
        if job is None:
            raise AppException(
                message="Job not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="JOB_NOT_FOUND",
            )
        return job

    @staticmethod
    def list_document_jobs(db: Session, document_id: UUID) -> list[ProcessingJob]:
        document = DocumentRepository.get_by_id(db, document_id)
        if document is None or document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="DOCUMENT_NOT_FOUND",
            )

        return ProcessingJobRepository.list_by_document_id(db, document_id)

    @staticmethod
    def list_workspace_jobs(db: Session, workspace_id: UUID) -> list[ProcessingJob]:
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if workspace is None:
            raise AppException(
                message="Workspace not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="WORKSPACE_NOT_FOUND",
            )

        return ProcessingJobRepository.list_by_workspace_id(db, workspace_id)

    @staticmethod
    def retry_job(db: Session, job_id: UUID) -> ProcessingJob:
        existing_job = ProcessingJobService.get_job(db, job_id)

        document = DocumentRepository.get_by_id(db, existing_job.document_id)
        if document is None:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="DOCUMENT_NOT_FOUND",
            )

        if document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Cannot retry processing for a deleted document.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="DOCUMENT_DELETED",
            )

        return ProcessingJobService.create_document_processing_job(db, document)
