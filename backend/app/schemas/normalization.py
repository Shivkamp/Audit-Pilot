from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NormalizedRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    document_id: UUID
    source_record_id: UUID
    record_category: str
    normalized_data: dict[str, Any]
    normalization_status: str
    normalization_confidence: float | None = None
    normalization_errors: list[dict[str, Any]] | None = None
    created_at: datetime
    updated_at: datetime


class NormalizedRecordListData(BaseModel):
    document_id: UUID
    total_records: int
    limit: int
    offset: int
    records: list[NormalizedRecordResponse]


class NormalizationSummaryData(BaseModel):
    document_id: UUID
    document_type: str
    total_records: int
    normalized: int
    partial: int
    failed: int
    skipped: int


class WorkspaceNormalizationDocumentSummary(BaseModel):
    document_id: UUID
    original_filename: str
    document_status: str
    document_type: str
    total_records: int
    normalized: int = 0
    partial: int = 0
    failed: int = 0
    skipped: int = 0


class WorkspaceNormalizationSummaryData(BaseModel):
    workspace_id: UUID
    documents: list[WorkspaceNormalizationDocumentSummary]


class NormalizeDocumentResponse(BaseModel):
    document_id: UUID
    document_type: str
    total_processed: int
    normalized: int
    partial: int
    failed: int
    skipped: int