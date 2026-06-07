from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ClassificationResultData(BaseModel):
    document_id: UUID
    original_filename: str
    status: str
    document_type: str
    classification_confidence: float | None = None
    classification_method: str | None = None
    classification_reason: dict[str, Any] | None = None
    classified_at: datetime | None = None


class DocumentClassificationResponse(ClassificationResultData):
    pass


class WorkspaceClassificationDocumentItem(BaseModel):
    document_id: UUID
    original_filename: str
    status: str
    document_type: str
    classification_confidence: float | None = None
    classified_at: datetime | None = None


class WorkspaceClassificationSummaryData(BaseModel):
    workspace_id: UUID
    documents: list[WorkspaceClassificationDocumentItem]
    counts_by_document_type: dict[str, int]
