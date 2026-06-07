from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, document_access_dependency, workspace_access_dependency
from app.core.config import settings
from app.core.responses import success_response
from app.schemas.extraction import (
    ExtractedRecordListData,
    ExtractedRecordResponse,
    ExtractionSummaryResponse,
    WorkspaceExtractionSummaryResponse,
)
from app.services.extraction_service import ExtractionService

router = APIRouter()


@router.get("/documents/{document_id}/extracted-records")
def get_document_extracted_records(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
    limit: int = Query(default=settings.extraction_api_default_limit, ge=1),
    offset: int = Query(default=0, ge=0),
    record_type: str | None = Query(default=None),
) -> dict:
    effective_limit = min(limit, settings.extraction_api_max_limit)
    extracted_data = ExtractionService.get_document_extracted_records(
        db,
        document_id=document_id,
        limit=effective_limit,
        offset=offset,
        record_type=record_type,
    )

    response_data = ExtractedRecordListData(
        document_id=extracted_data["document_id"],
        total_records=extracted_data["total_records"],
        limit=extracted_data["limit"],
        offset=extracted_data["offset"],
        records=[
            ExtractedRecordResponse.model_validate(record)
            for record in extracted_data["records"]
        ],
    )

    return success_response(
        message="Extracted records fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/documents/{document_id}/extraction-summary")
def get_document_extraction_summary(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
) -> dict:
    summary = ExtractionService.get_document_extraction_summary(db, document_id)
    response_data = ExtractionSummaryResponse(**summary)

    return success_response(
        message="Document extraction summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/extraction-summary")
def get_workspace_extraction_summary(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    summary = ExtractionService.get_workspace_extraction_summary(db, workspace_id)
    response_data = WorkspaceExtractionSummaryResponse(**summary)

    return success_response(
        message="Workspace extraction summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )
