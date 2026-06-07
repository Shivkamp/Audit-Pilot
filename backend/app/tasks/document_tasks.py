from __future__ import annotations

from uuid import UUID

from app.celery_app import celery_app
from app.core.constants import (
    DOCUMENT_STATUS_FAILED,
    DOCUMENT_STATUS_PROCESSING,
    DOCUMENT_STATUS_PROCESSED,
    JOB_STATUS_CLASSIFYING,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_EMBEDDING,
    JOB_STATUS_EXTRACTING,
    JOB_STATUS_FAILED,
    JOB_STATUS_NORMALIZING,
    JOB_STATUS_RUNNING_RISK_CHECKS,
    JOB_STATUS_STARTED,
)
from app.core.exceptions import AppException
from app.core.logging import logger
from app.db.base import Base  # noqa: F401 — registers all ORM models in this process
from app.db.session import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.repositories.normalization_repository import NormalizationRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.services.classification_service import ClassificationService
from app.services.extraction_service import ExtractionService
from app.services.knowledge_index_service import KnowledgeIndexService
from app.services.normalization_service import NormalizationService
from app.services.risk_engine_service import RiskEngineService

_CONTROLLED_FAILURE_STEP = "Document processing failed"
_CONTROLLED_INTERNAL_FAILURE_MESSAGE = "Document processing failed due to an internal processing error."


@celery_app.task(name="app.tasks.document_tasks.process_document_task")
def process_document_task(job_id: str) -> None:
    db = SessionLocal()
    job = None

    try:
        try:
            parsed_job_id = UUID(job_id)
        except ValueError:
            logger.warning("Invalid processing job id received by worker: %s", job_id)
            return

        job = ProcessingJobRepository.get_by_id(db, parsed_job_id)
        if job is None:
            logger.warning("Processing job not found for job_id=%s", job_id)
            return

        document = DocumentRepository.get_by_id(db, job.document_id)
        if document is None:
            logger.warning("Document not found for processing job_id=%s", job_id)
            ProcessingJobRepository.update_status(
                db,
                job,
                status=JOB_STATUS_FAILED,
                current_step=_CONTROLLED_FAILURE_STEP,
                error_message="Document not found.",
            )
            return

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_STARTED,
            progress_percent=10,
            current_step="Document processing started",
            error_message=None,
        )

        DocumentRepository.update_status(db, document, DOCUMENT_STATUS_PROCESSING)

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_EXTRACTING,
            progress_percent=20,
            current_step="Extracting document content",
            error_message=None,
        )

        # Clean up normalized records before re-extraction to avoid FK
        # constraint violation (normalized_records.source_record_id
        # references extracted_records.id).
        NormalizationRepository.delete_records_by_document(db, document.id)

        ExtractionService.extract_document(db, document.id, job.id)

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_CLASSIFYING,
            progress_percent=80,
            current_step="Classifying document type",
            error_message=None,
        )

        ClassificationService.classify_document(db, document.id)

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_NORMALIZING,
            progress_percent=90,
            current_step="Normalizing extracted records",
            error_message=None,
        )

        NormalizationService.normalize_document(db, document.id)

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_RUNNING_RISK_CHECKS,
            progress_percent=93,
            current_step="Running risk checks",
            error_message=None,
        )

        RiskEngineService.run_workspace_risks(db, document.workspace_id)

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_EMBEDDING,
            progress_percent=96,
            current_step="Building knowledge index",
            error_message=None,
        )

        KnowledgeIndexService.index_document(db, document.id)

        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_COMPLETED,
            progress_percent=100,
            current_step="Document processing completed",
            error_message=None,
        )
        DocumentRepository.update_status(db, document, DOCUMENT_STATUS_PROCESSED)
    except AppException as exc:
        logger.warning(
            "Controlled extraction failure for job_id=%s error_code=%s",
            job_id,
            exc.error_code,
        )
        db.rollback()
        if job is not None:
            _mark_failed(db, job_id=job_id, job=job, safe_error_message=exc.message)
    except Exception:
        logger.exception("Processing task failed for job_id=%s", job_id)
        db.rollback()
        if job is not None:
            _mark_failed(
                db,
                job_id=job_id,
                job=job,
                safe_error_message=_CONTROLLED_INTERNAL_FAILURE_MESSAGE,
            )
    finally:
        db.close()


def _mark_failed(db, *, job_id: str, job, safe_error_message: str) -> None:
    document = DocumentRepository.get_by_id(db, job.document_id)

    try:
        ProcessingJobRepository.update_status(
            db,
            job,
            status=JOB_STATUS_FAILED,
            current_step=_CONTROLLED_FAILURE_STEP,
            error_message=safe_error_message,
        )
        if document is not None:
            DocumentRepository.update_status(db, document, DOCUMENT_STATUS_FAILED)
    except Exception:
        logger.exception("Failed to persist failed status for job_id=%s", job_id)
