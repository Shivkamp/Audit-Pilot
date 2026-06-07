from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import (
    DbSession,
    document_access_dependency,
    job_access_dependency,
    workspace_access_dependency,
)
from app.core.constants import WORKSPACE_WRITE_ROLES
from app.core.responses import success_response
from app.schemas.processing_job import ProcessingJobResponse
from app.services.processing_job_service import ProcessingJobService

router = APIRouter()


def _serialize_job(job: object) -> dict:
    return ProcessingJobResponse.model_validate(job).model_dump(mode="json")


@router.get("/jobs/{job_id}")
def get_job(
    job_id: UUID,
    db: DbSession,
    _: object = Depends(job_access_dependency()),
) -> dict:
    job = ProcessingJobService.get_job(db, job_id)
    return success_response(
        message="Job fetched successfully",
        data=_serialize_job(job),
    )


@router.get("/documents/{document_id}/jobs")
def list_document_jobs(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
) -> dict:
    jobs = ProcessingJobService.list_document_jobs(db, document_id)
    return success_response(
        message="Document jobs fetched successfully",
        data=[_serialize_job(job) for job in jobs],
    )


@router.get("/workspaces/{workspace_id}/jobs")
def list_workspace_jobs(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    jobs = ProcessingJobService.list_workspace_jobs(db, workspace_id)
    return success_response(
        message="Workspace jobs fetched successfully",
        data=[_serialize_job(job) for job in jobs],
    )


@router.post("/jobs/{job_id}/retry")
def retry_job(
    job_id: UUID,
    db: DbSession,
    _: object = Depends(job_access_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    retried_job = ProcessingJobService.retry_job(db, job_id)
    return success_response(
        message="Job retried successfully",
        data=_serialize_job(retried_job),
    )
