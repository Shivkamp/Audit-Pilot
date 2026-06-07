from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractedRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    workspace_id: UUID
    record_type: str
    page_number: int | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    column_name: str | None = None
    raw_text: str | None = None
    raw_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class ExtractedRecordListData(BaseModel):
    document_id: UUID
    total_records: int
    limit: int
    offset: int
    records: list[ExtractedRecordResponse]


class ExtractionSummaryResponse(BaseModel):
    document_id: UUID
    total_records: int
    text_records: int
    excel_rows: int
    csv_rows: int
    table_rows: int
    metadata_records: int
    pages_detected: list[int]
    sheets_detected: list[str]


class WorkspaceDocumentExtractionSummary(BaseModel):
    document_id: UUID
    original_filename: str
    document_status: str
    total_extracted_records: int
    text_records: int = 0
    excel_rows: int = 0
    csv_rows: int = 0
    table_rows: int = 0
    metadata_records: int = 0


class WorkspaceExtractionSummaryResponse(BaseModel):
    workspace_id: UUID
    documents: list[WorkspaceDocumentExtractionSummary]
