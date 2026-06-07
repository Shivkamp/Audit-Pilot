from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import (
    DbSession,
    document_access_dependency,
    workspace_access_dependency,
    workspace_role_dependency,
)
from app.core.constants import WORKSPACE_ADMIN_ROLES, WORKSPACE_WRITE_ROLES
from app.core.responses import success_response
from app.schemas.document import DocumentDownloadUrlResponse, DocumentResponse
from app.schemas.processing_job import ProcessingJobResponse
from app.services.document_service import DocumentService

router = APIRouter()


def _serialize_document(document: object) -> dict:
    return DocumentResponse.model_validate(document).model_dump(mode="json")


def _serialize_job(job: object) -> dict:
    return ProcessingJobResponse.model_validate(job).model_dump(mode="json")


@router.post("/workspaces/{workspace_id}/documents/upload")
def upload_document(
    workspace_id: UUID,
    db: DbSession,
    file: UploadFile = File(...),
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    document, processing_job = DocumentService.upload_document(db, workspace_id, file)
    return success_response(
        message="Document uploaded successfully",
        data={
            "document": _serialize_document(document),
            "processing_job": _serialize_job(processing_job),
        },
    )


@router.post("/workspaces/{workspace_id}/documents/upload-folder")
def upload_folder(
    workspace_id: UUID,
    db: DbSession,
    files: list[UploadFile] = File(...),
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    results = []
    for file in files:
        document, processing_job = DocumentService.upload_document(db, workspace_id, file)
        results.append(
            {
                "document": _serialize_document(document),
                "processing_job": _serialize_job(processing_job),
            }
        )
    return success_response(
        message=f"{len(results)} document(s) uploaded and queued for processing.",
        data=results,
    )


@router.get("/workspaces/{workspace_id}/documents")
def list_workspace_documents(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    documents = DocumentService.list_workspace_documents(db, workspace_id)
    return success_response(
        message="Documents fetched successfully.",
        data=[_serialize_document(document) for document in documents],
    )


@router.get("/documents/{document_id}")
def get_document(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
) -> dict:
    document = DocumentService.get_document(db, document_id)
    return success_response(
        message="Document fetched successfully.",
        data=_serialize_document(document),
    )


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(
        document_access_dependency(
            allowed_roles=WORKSPACE_ADMIN_ROLES,
            include_deleted=True,
        )
    ),
) -> dict:
    document = DocumentService.delete_document(db, document_id)
    return success_response(
        message="Document deleted successfully.",
        data=_serialize_document(document),
    )


@router.get("/documents/{document_id}/download-url")
def get_document_download_url(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
) -> dict:
    response = DocumentService.generate_download_url(db, document_id)
    return success_response(
        message="Download URL generated successfully",
        data=DocumentDownloadUrlResponse.model_validate(response).model_dump(mode="json"),
    )
