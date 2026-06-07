from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.constants import JOB_STATUS_PENDING, JOB_TYPE_DOCUMENT_PROCESSING


class ProcessingJobBase(BaseModel):
    document_id: UUID
    workspace_id: UUID
    job_type: str = JOB_TYPE_DOCUMENT_PROCESSING
    status: str = JOB_STATUS_PENDING
    celery_task_id: str | None = None
    progress_percent: int = 0
    current_step: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ProcessingJobResponse(ProcessingJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
