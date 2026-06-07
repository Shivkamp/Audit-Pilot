from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, document_access_dependency, workspace_access_dependency
from app.core.constants import WORKSPACE_WRITE_ROLES
from app.core.responses import success_response
from app.schemas.classification import (
    DocumentClassificationResponse,
    WorkspaceClassificationSummaryData,
)
from app.services.classification_service import ClassificationService

router = APIRouter()


@router.get("/documents/{document_id}/classification")
def get_document_classification(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
) -> dict:
    classification = ClassificationService.get_document_classification(db, document_id)
    response_data = DocumentClassificationResponse(**classification)

    return success_response(
        message="Document classification fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.post("/documents/{document_id}/classify")
def classify_document(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    classification = ClassificationService.classify_document(db, document_id)
    response_data = DocumentClassificationResponse(**classification)

    return success_response(
        message="Document classified successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/classification-summary")
def get_workspace_classification_summary(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    summary = ClassificationService.get_workspace_classification_summary(db, workspace_id)
    response_data = WorkspaceClassificationSummaryData(**summary)

    return success_response(
        message="Workspace classification summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )
