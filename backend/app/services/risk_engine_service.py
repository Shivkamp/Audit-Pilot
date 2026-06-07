from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    ALLOWED_RISK_STATUSES,
    RISK_ENGINE_FAILED,
    RISK_FINDING_NOT_FOUND,
    RISK_INVALID_STATUS,
    RISK_STATUS_OPEN,
)
from app.core.exceptions import AppException
from app.models.normalized_record import NormalizedRecord
from app.models.risk_finding import RiskFinding
from app.repositories.normalization_repository import NormalizationRepository
from app.repositories.risk_finding_repository import RiskFindingRepository
from app.risk_engine.engine import RiskEngine
from app.risk_engine.base import RiskRuleFinding
from app.services.document_service import DocumentService
from app.services.risk_rule_config_service import RiskRuleConfigService
from app.services.workspace_service import WorkspaceService


class RiskEngineService:
    @staticmethod
    def run_workspace_risks(db: Session, workspace_id: UUID) -> dict:
        try:
            workspace = WorkspaceService.get_workspace(db, workspace_id)
            RiskRuleConfigService.initialize_defaults_for_workspace(db, workspace.id)
            config_map = RiskRuleConfigService.get_config_map_for_workspace(db, workspace.id)

            normalized_records = NormalizationRepository.get_by_workspace_id(db, workspace.id)
            records_by_category = RiskEngineService._group_records_by_category(normalized_records)

            RiskFindingRepository.delete_by_workspace_id(db, workspace.id)

            engine = RiskEngine(
                short_deposit_critical_threshold=settings.risk_short_deposit_critical_threshold,
                workspace_id=workspace.id,
                config_by_rule_key=config_map,
            )
            findings = engine.run(records_by_category)
            payloads = [
                RiskEngineService._build_finding_payload(workspace_id=workspace.id, finding=finding)
                for finding in findings
            ]
            created_count = RiskFindingRepository.bulk_create(db, payloads)
            summary = RiskFindingRepository.get_summary_by_workspace(db, workspace.id)

            return {
                "workspace_id": workspace.id,
                "total_findings": created_count,
                "summary": summary,
            }
        except AppException:
            raise
        except Exception as exc:
            raise AppException(
                message="Risk checks failed due to an internal processing error.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=RISK_ENGINE_FAILED,
            ) from exc

    @staticmethod
    def list_workspace_findings(
        db: Session,
        workspace_id: UUID,
        *,
        risk_type: str | None,
        severity: str | None,
        status_filter: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        safe_limit = max(1, min(limit, settings.risk_api_max_limit))
        safe_offset = max(0, offset)

        findings = RiskFindingRepository.list_by_workspace(
            db,
            workspace.id,
            risk_type=risk_type,
            severity=severity,
            status=status_filter,
            limit=safe_limit,
            offset=safe_offset,
        )
        total_records = RiskFindingRepository.count_by_workspace(
            db,
            workspace.id,
            risk_type=risk_type,
            severity=severity,
            status=status_filter,
        )

        return {
            "workspace_id": workspace.id,
            "total_records": total_records,
            "limit": safe_limit,
            "offset": safe_offset,
            "findings": findings,
        }

    @staticmethod
    def list_document_findings(
        db: Session,
        document_id: UUID,
        *,
        risk_type: str | None,
        severity: str | None,
        status_filter: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        document = DocumentService.get_document(db, document_id)

        safe_limit = max(1, min(limit, settings.risk_api_max_limit))
        safe_offset = max(0, offset)

        findings = RiskFindingRepository.list_by_document(
            db,
            document.id,
            risk_type=risk_type,
            severity=severity,
            status=status_filter,
            limit=safe_limit,
            offset=safe_offset,
        )
        total_records = RiskFindingRepository.count_by_document(
            db,
            document.id,
            risk_type=risk_type,
            severity=severity,
            status=status_filter,
        )

        return {
            "document_id": document.id,
            "total_records": total_records,
            "limit": safe_limit,
            "offset": safe_offset,
            "findings": findings,
        }

    @staticmethod
    def get_workspace_summary(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        return RiskFindingRepository.get_summary_by_workspace(db, workspace.id)

    @staticmethod
    def update_finding_status(db: Session, finding_id: UUID, status_value: str) -> RiskFinding:
        if status_value not in ALLOWED_RISK_STATUSES:
            raise AppException(
                message="Invalid risk finding status.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=RISK_INVALID_STATUS,
            )

        finding = RiskFindingRepository.get_by_id(db, finding_id)
        if finding is None:
            raise AppException(
                message="Risk finding not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=RISK_FINDING_NOT_FOUND,
            )

        return RiskFindingRepository.update_status(db, finding, status_value)

    @staticmethod
    def _group_records_by_category(
        records: list[NormalizedRecord],
    ) -> dict[str, list[NormalizedRecord]]:
        grouped: dict[str, list[NormalizedRecord]] = defaultdict(list)
        for record in records:
            grouped[record.record_category].append(record)
        return dict(grouped)

    @staticmethod
    def _build_finding_payload(workspace_id: UUID, finding: RiskRuleFinding) -> dict:
        related_ids = (
            [str(record_id) for record_id in dict.fromkeys(finding.related_normalized_record_ids)]
            if finding.related_normalized_record_ids
            else None
        )

        return {
            "workspace_id": workspace_id,
            "document_id": finding.document_id,
            "primary_normalized_record_id": finding.primary_normalized_record_id,
            "related_normalized_record_ids": related_ids,
            "risk_type": finding.risk_type,
            "severity": finding.severity,
            "title": finding.title,
            "description": finding.description,
            "risk_data": finding.risk_data,
            "status": RISK_STATUS_OPEN,
        }
