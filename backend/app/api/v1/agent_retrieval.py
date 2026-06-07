from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, workspace_access_dependency
from app.core.config import settings
from app.core.responses import success_response
from app.schemas.agent_retrieval import (
    AgentEvidenceRequest,
    AgentEvidenceResponse,
    RiskEvidenceRequest,
    FindingContextResponse,
    SourceTraceResponse,
)
from app.services.agent_retrieval_service import AgentRetrievalService

router = APIRouter()


@router.post("/workspaces/{workspace_id}/agent-retrieval/evidence")
def retrieve_workspace_agent_evidence(
    workspace_id: UUID,
    payload: AgentEvidenceRequest,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    effective_limit = min(payload.limit, settings.agent_retrieval_max_limit)
    result = AgentRetrievalService.retrieve_workspace_evidence(
        db,
        workspace_id,
        query=payload.query,
        limit=effective_limit,
        include_source_trace=payload.include_source_trace,
    )
    response_data = AgentEvidenceResponse(**result)

    return success_response(
        message="Workspace agent evidence retrieved successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.post("/workspaces/{workspace_id}/agent-retrieval/risk-evidence")
def retrieve_workspace_risk_evidence(
    workspace_id: UUID,
    payload: RiskEvidenceRequest,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    effective_limit = min(payload.limit, settings.agent_retrieval_max_limit)
    result = AgentRetrievalService.retrieve_risk_evidence(
        db,
        workspace_id,
        risk_type=payload.risk_type,
        query=payload.query,
        limit=effective_limit,
        include_source_trace=payload.include_source_trace,
    )
    response_data = AgentEvidenceResponse(**result)

    return success_response(
        message="Workspace risk evidence retrieved successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/agent-retrieval/risk-findings/{risk_finding_id}/context")
def get_risk_finding_context(
    workspace_id: UUID,
    risk_finding_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    result = AgentRetrievalService.get_finding_context(db, workspace_id, risk_finding_id)
    response_data = FindingContextResponse(**result)

    return success_response(
        message="Risk finding context fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/source-trace/{source_type}/{source_id}")
def get_workspace_source_trace(
    workspace_id: UUID,
    source_type: str,
    source_id: str,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    trace = AgentRetrievalService.get_source_trace(
        db,
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
    )
    response_data = SourceTraceResponse(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        trace=trace,
    )

    return success_response(
        message="Source trace resolved successfully.",
        data=response_data.model_dump(mode="json"),
    )
