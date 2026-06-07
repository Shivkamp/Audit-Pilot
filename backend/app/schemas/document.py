from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.constants import (
    DOCUMENT_STATUS_UPLOADED,
    DOCUMENT_TYPE_UNKNOWN,
    DOCUMENT_UPLOAD_SOURCE_MANUAL,
)


class DocumentBase(BaseModel):
    workspace_id: UUID
    original_filename: str
    stored_filename: str
    file_extension: str
    content_type: str | None = None
    file_size_bytes: int
    storage_backend: str
    storage_bucket: str | None = None
    storage_key: str
    document_type: str = DOCUMENT_TYPE_UNKNOWN
    classification_confidence: float | None = None
    classification_method: str | None = None
    classification_reason: dict[str, Any] | None = None
    classified_at: datetime | None = None
    status: str = DOCUMENT_STATUS_UPLOADED
    upload_source: str = DOCUMENT_UPLOAD_SOURCE_MANUAL


class DocumentCreate(DocumentBase):
    id: UUID


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class DocumentDownloadUrlResponse(BaseModel):
    document_id: UUID
    download_url: str
    expires_in_seconds: int
