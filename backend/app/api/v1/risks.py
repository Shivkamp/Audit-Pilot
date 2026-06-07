from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    DbSession,
    document_access_dependency,
    risk_finding_access_dependency,
    workspace_access_dependency,
    workspace_role_dependency,
)
from app.core.config import settings
from app.core.constants import WORKSPACE_WRITE_ROLES
from app.core.responses import success_response
from app.schemas.risk import (
    RiskFindingListResponse,
    RiskFindingResponse,
    RiskFindingStatusUpdate,
    RiskRunResponse,
    RiskSummaryResponse,
)
from app.services.risk_engine_service import RiskEngineService

router = APIRouter()


@router.post("/workspaces/{workspace_id}/risk-checks/run")
def run_workspace_risk_checks(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    result = RiskEngineService.run_workspace_risks(db, workspace_id)
    summary_data = RiskSummaryResponse(**result["summary"])
    response_data = RiskRunResponse(
        workspace_id=result["workspace_id"],
        total_findings=result["total_findings"],
        summary=summary_data,
    )

    return success_response(
        message="Workspace risk checks completed successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/risk-findings")
def list_workspace_risk_findings(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
    risk_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=settings.risk_api_default_limit, ge=1),
    offset: int = Query(default=0, ge=0),
) -> dict:
    effective_limit = min(limit, settings.risk_api_max_limit)
    findings_data = RiskEngineService.list_workspace_findings(
        db,
        workspace_id,
        risk_type=risk_type,
        severity=severity,
        status_filter=status,
        limit=effective_limit,
        offset=offset,
    )

    response_data = RiskFindingListResponse(
        workspace_id=findings_data["workspace_id"],
        total_records=findings_data["total_records"],
        limit=findings_data["limit"],
        offset=findings_data["offset"],
        findings=[
            RiskFindingResponse.model_validate(finding)
            for finding in findings_data["findings"]
        ],
    )

    return success_response(
        message="Workspace risk findings fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/documents/{document_id}/risk-findings")
def list_document_risk_findings(
    document_id: UUID,
    db: DbSession,
    _: object = Depends(document_access_dependency()),
    risk_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=settings.risk_api_default_limit, ge=1),
    offset: int = Query(default=0, ge=0),
) -> dict:
    effective_limit = min(limit, settings.risk_api_max_limit)
    findings_data = RiskEngineService.list_document_findings(
        db,
        document_id,
        risk_type=risk_type,
        severity=severity,
        status_filter=status,
        limit=effective_limit,
        offset=offset,
    )

    response_data = RiskFindingListResponse(
        document_id=findings_data["document_id"],
        total_records=findings_data["total_records"],
        limit=findings_data["limit"],
        offset=findings_data["offset"],
        findings=[
            RiskFindingResponse.model_validate(finding)
            for finding in findings_data["findings"]
        ],
    )

    return success_response(
        message="Document risk findings fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/risk-summary")
def get_workspace_risk_summary(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    summary = RiskEngineService.get_workspace_summary(db, workspace_id)
    response_data = RiskSummaryResponse(**summary)

    return success_response(
        message="Workspace risk summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.patch("/risk-findings/{finding_id}/status")
def update_risk_finding_status(
    finding_id: UUID,
    payload: RiskFindingStatusUpdate,
    db: DbSession,
    _: object = Depends(risk_finding_access_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    updated_finding = RiskEngineService.update_finding_status(db, finding_id, payload.status)
    response_data = RiskFindingResponse.model_validate(updated_finding)

    return success_response(
        message="Risk finding status updated successfully.",
        data=response_data.model_dump(mode="json"),
    )
