from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, document_access_dependency, workspace_access_dependency
from app.core.config import settings
from app.core.constants import WORKSPACE_WRITE_ROLES
from app.core.responses import success_response
from app.schemas.normalization import (
    NormalizeDocumentResponse,
    NormalizationSummaryData,
    NormalizedRecordListData,
    NormalizedRecordResponse,
    WorkspaceNormalizationSummaryData,
)
from app.services.normalization_service import NormalizationService

router = APIRouter()


@router.get("/documents/{document_id}/normalized-records")
def get_document_normalized_records(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
    limit: int = Query(default=settings.normalization_api_default_limit, ge=1),
    offset: int = Query(default=0, ge=0),
    record_category: str | None = Query(default=None),
    normalization_status: str | None = Query(default=None),
) -> dict:
    effective_limit = min(limit, settings.normalization_api_max_limit)
    normalized_data = NormalizationService.get_document_normalized_records(
        db,
        document_id=document_id,
        limit=effective_limit,
        offset=offset,
        record_category=record_category,
        normalization_status=normalization_status,
    )

    response_data = NormalizedRecordListData(
        document_id=normalized_data["document_id"],
        total_records=normalized_data["total_records"],
        limit=normalized_data["limit"],
        offset=normalized_data["offset"],
        records=[
            NormalizedRecordResponse.model_validate(record)
            for record in normalized_data["records"]
        ],
    )

    return success_response(
        message="Normalized records fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/documents/{document_id}/normalization-summary")
def get_document_normalization_summary(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
) -> dict:
    summary = NormalizationService.get_document_normalization_summary(db, document_id)
    response_data = NormalizationSummaryData(**summary)

    return success_response(
        message="Document normalization summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.post("/documents/{document_id}/normalize")
def normalize_document(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    summary = NormalizationService.normalize_document(db, document_id)
    response_data = NormalizeDocumentResponse(**summary)

    return success_response(
        message="Document normalized successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/normalization-summary")
def get_workspace_normalization_summary(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    summary = NormalizationService.get_workspace_normalization_summary(db, workspace_id)
    response_data = WorkspaceNormalizationSummaryData(**summary)

    return success_response(
        message="Workspace normalization summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )