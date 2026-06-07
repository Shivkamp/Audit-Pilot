from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_STARTED
from app.models.processing_job import ProcessingJob


class ProcessingJobRepository:
    @staticmethod
    def create(db: Session, job_data: dict) -> ProcessingJob:
        job = ProcessingJob(**job_data)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_by_id(db: Session, job_id: UUID) -> ProcessingJob | None:
        return db.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id))

    @staticmethod
    def list_by_document_id(db: Session, document_id: UUID) -> list[ProcessingJob]:
        statement = (
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        return list(db.scalars(statement))

    @staticmethod
    def list_by_workspace_id(db: Session, workspace_id: UUID) -> list[ProcessingJob]:
        statement = (
            select(ProcessingJob)
            .where(ProcessingJob.workspace_id == workspace_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        return list(db.scalars(statement))

    @staticmethod
    def update_status(
        db: Session,
        job: ProcessingJob,
        status: str,
        current_step: str | None = None,
        progress_percent: int | None = None,
        error_message: str | None = None,
    ) -> ProcessingJob:
        job.status = status
        if current_step is not None:
            job.current_step = current_step
        if progress_percent is not None:
            job.progress_percent = progress_percent
        # Only set error_message when explicitly provided; for non-failure
        # statuses with no message supplied, clear any previous error.
        if error_message is not None:
            job.error_message = error_message
        elif status != JOB_STATUS_FAILED:
            job.error_message = None

        if status == JOB_STATUS_STARTED and job.started_at is None:
            job.started_at = datetime.now(timezone.utc)

        if status in {JOB_STATUS_COMPLETED, JOB_STATUS_FAILED}:
            job.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def set_celery_task_id(db: Session, job: ProcessingJob, celery_task_id: str) -> ProcessingJob:
        job.celery_task_id = celery_task_id
        db.commit()
        db.refresh(job)
        return job
