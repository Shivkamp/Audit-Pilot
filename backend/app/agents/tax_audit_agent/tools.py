from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    AGENT_CHAT_INVALID_INPUT,
    AGENT_CHAT_UNSUPPORTED_SOURCE_TYPE,
    KNOWLEDGE_SOURCE_TYPE_EXTRACTED_RECORD,
    KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
    KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
    RISK_TYPE_DUPLICATE_INVOICE,
    RISK_TYPE_HIGH_VALUE_TRANSACTION,
    RISK_TYPE_MISSING_PAN,
    RISK_TYPE_MISSING_SUPPORTING_DOCUMENT,
    RISK_TYPE_SHORT_DEPOSIT,
    RISK_TYPE_TDS_MISMATCH,
    RISK_TYPE_VENDOR_NAME_MISMATCH,
    RISK_TYPE_WRONG_TDS_SECTION,
)
from app.core.exceptions import AppException
from app.repositories.risk_finding_repository import RiskFindingRepository
from app.services.agent_retrieval_service import AgentRetrievalService
from app.services.risk_engine_service import RiskEngineService
from app.services.workspace_service import WorkspaceService

_RISK_KEYWORDS_TO_TYPE: dict[str, str] = {
    "missing pan": RISK_TYPE_MISSING_PAN,
    "pan missing": RISK_TYPE_MISSING_PAN,
    "duplicate invoice": RISK_TYPE_DUPLICATE_INVOICE,
    "dup invoice": RISK_TYPE_DUPLICATE_INVOICE,
    "tds mismatch": RISK_TYPE_TDS_MISMATCH,
    "mismatch": RISK_TYPE_TDS_MISMATCH,
    "short deposit": RISK_TYPE_SHORT_DEPOSIT,
    "vendor name mismatch": RISK_TYPE_VENDOR_NAME_MISMATCH,
    "wrong tds section": RISK_TYPE_WRONG_TDS_SECTION,
    "high value": RISK_TYPE_HIGH_VALUE_TRANSACTION,
    "supporting document": RISK_TYPE_MISSING_SUPPORTING_DOCUMENT,
}


class TaxAuditAgentTools:
    def __init__(self, db: Session) -> None:
        self.db = db

    def check_workspace_ready(self, workspace_id: str) -> dict[str, Any]:
        workspace_uuid = self._as_uuid(workspace_id, field_name="workspace_id")
        workspace = WorkspaceService.get_workspace(self.db, workspace_uuid)
        summary = RiskFindingRepository.get_summary_by_workspace(self.db, workspace.id)
        total_findings = int(summary.get("total_findings") or 0)

        return {
            "workspace_id": str(workspace.id),
            "ready": total_findings > 0,
            "total_findings": total_findings,
        }

    def get_risk_summary(self, workspace_id: str, *, limit: int | None = None) -> dict[str, Any]:
        workspace_uuid = self._as_uuid(workspace_id, field_name="workspace_id")
        summary = RiskEngineService.get_workspace_summary(self.db, workspace_uuid)
        safe_limit = self._safe_limit(limit)
        findings_data = RiskEngineService.list_workspace_findings(
            self.db,
            workspace_uuid,
            risk_type=None,
            severity=None,
            status_filter=None,
            limit=safe_limit,
            offset=0,
        )

        return {
            "risk_summary": self._to_serializable(summary),
            "risk_findings": [
                self._serialize_risk_finding(finding)
                for finding in findings_data.get("findings") or []
            ],
        }

    def list_risk_findings(
        self,
        workspace_id: str,
        *,
        risk_type: str | None = None,
        severity: str | None = None,
        status_filter: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> dict[str, Any]:
        workspace_uuid = self._as_uuid(workspace_id, field_name="workspace_id")
        # Findings listing is lightweight metadata — cap at listing_max_limit (not
        # agent_max_evidence which is meant for heavier evidence chunks).
        requested = int(limit) if limit is not None else int(settings.agent_listing_max_limit)
        safe_limit = max(1, min(requested, int(settings.agent_listing_max_limit)))

        findings_data = RiskEngineService.list_workspace_findings(
            self.db,
            workspace_uuid,
            risk_type=risk_type,
            severity=severity,
            status_filter=status_filter,
            limit=safe_limit,
            offset=max(0, int(offset)),
        )

        return {
            "workspace_id": str(findings_data.get("workspace_id") or workspace_uuid),
            "total_records": int(findings_data.get("total_records") or 0),
            "limit": safe_limit,
            "offset": max(0, int(offset)),
            "findings": [
                self._serialize_risk_finding(finding)
                for finding in findings_data.get("findings") or []
            ],
        }

    def retrieve_workspace_evidence(
        self,
        workspace_id: str,
        *,
        query: str,
        limit: int | None,
        include_source_trace: bool,
    ) -> dict[str, Any]:
        workspace_uuid = self._as_uuid(workspace_id, field_name="workspace_id")
        safe_limit = self._safe_limit(limit)

        payload = AgentRetrievalService.retrieve_workspace_evidence(
            self.db,
            workspace_uuid,
            query=query,
            limit=safe_limit,
            include_source_trace=include_source_trace,
        )
        return self._to_serializable(payload)

    def retrieve_risk_evidence(
        self,
        workspace_id: str,
        *,
        query: str,
        limit: int | None,
        include_source_trace: bool,
        risk_type: str | None = None,
    ) -> dict[str, Any]:
        workspace_uuid = self._as_uuid(workspace_id, field_name="workspace_id")
        safe_limit = self._safe_limit(limit)
        resolved_risk_type = risk_type or self.infer_risk_type_from_text(query)

        if resolved_risk_type is None:
            summary = RiskFindingRepository.get_summary_by_workspace(self.db, workspace_uuid)
            counts_by_risk_type = summary.get("counts_by_risk_type") or {}
            if isinstance(counts_by_risk_type, dict) and counts_by_risk_type:
                resolved_risk_type = sorted(
                    counts_by_risk_type.items(),
                    key=lambda item: (-int(item[1]), str(item[0])),
                )[0][0]

        if resolved_risk_type:
            payload = AgentRetrievalService.retrieve_risk_evidence(
                self.db,
                workspace_uuid,
                risk_type=resolved_risk_type,
                query=query,
                limit=safe_limit,
                include_source_trace=include_source_trace,
            )
            return self._to_serializable(payload)

        return self.retrieve_workspace_evidence(
            workspace_id=workspace_id,
            query=query,
            limit=safe_limit,
            include_source_trace=include_source_trace,
        )

    def get_source_trace(self, workspace_id: str, source_type: str, source_id: str) -> dict[str, Any]:
        workspace_uuid = self._as_uuid(workspace_id, field_name="workspace_id")
        clean_source_type = (source_type or "").strip().lower()
        if clean_source_type not in {
            KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
            KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
            KNOWLEDGE_SOURCE_TYPE_EXTRACTED_RECORD,
        }:
            raise AppException(
                message="Unsupported source type for source trace.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=AGENT_CHAT_UNSUPPORTED_SOURCE_TYPE,
            )

        trace = AgentRetrievalService.get_source_trace(
            self.db,
            workspace_id=workspace_uuid,
            source_type=clean_source_type,
            source_id=source_id,
        )
        return self._to_serializable(trace)

    def infer_risk_type_from_text(self, text: str) -> str | None:
        clean_text = (text or "").strip().lower()
        for keyword, risk_type in _RISK_KEYWORDS_TO_TYPE.items():
            if keyword in clean_text:
                return risk_type

        return None

    def _safe_limit(self, limit: int | None) -> int:
        requested = int(limit) if limit is not None else int(settings.agent_max_evidence)
        return max(
            1,
            min(
                requested,
                int(settings.agent_max_evidence),
                int(settings.agent_retrieval_max_limit),
            ),
        )

    def _as_uuid(self, value: str, *, field_name: str) -> UUID:
        try:
            return UUID(str(value))
        except (ValueError, TypeError) as exc:
            raise AppException(
                message=f"Invalid {field_name}.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=AGENT_CHAT_INVALID_INPUT,
            ) from exc

    def _serialize_risk_finding(self, finding: object) -> dict[str, Any]:
        data = {
            "id": getattr(finding, "id", None),
            "workspace_id": getattr(finding, "workspace_id", None),
            "document_id": getattr(finding, "document_id", None),
            "primary_normalized_record_id": getattr(finding, "primary_normalized_record_id", None),
            "related_normalized_record_ids": getattr(finding, "related_normalized_record_ids", None),
            "risk_type": getattr(finding, "risk_type", None),
            "severity": getattr(finding, "severity", None),
            "title": getattr(finding, "title", None),
            "description": getattr(finding, "description", None),
            "risk_data": getattr(finding, "risk_data", None),
            "status": getattr(finding, "status", None),
            "created_at": getattr(finding, "created_at", None),
            "updated_at": getattr(finding, "updated_at", None),
        }
        return self._to_serializable(data)

    def _to_serializable(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            return {str(key): self._to_serializable(value) for key, value in payload.items()}
        if isinstance(payload, list):
            return [self._to_serializable(item) for item in payload]
        if isinstance(payload, tuple):
            return [self._to_serializable(item) for item in payload]
        if isinstance(payload, UUID):
            return str(payload)
        if hasattr(payload, "isoformat"):
            try:
                return payload.isoformat()
            except Exception:
                return str(payload)
        return payload
