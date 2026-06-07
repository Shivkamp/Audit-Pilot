from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.risk_finding import RiskFinding


class RiskFindingRepository:
    @staticmethod
    def create(db: Session, payload: dict) -> RiskFinding:
        finding = RiskFinding(**payload)
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return finding

    @staticmethod
    def bulk_create(db: Session, payloads: Sequence[dict]) -> int:
        if not payloads:
            return 0

        findings = [RiskFinding(**payload) for payload in payloads]
        db.add_all(findings)
        db.commit()
        return len(findings)

    @staticmethod
    def get_by_id(db: Session, finding_id: UUID) -> RiskFinding | None:
        return db.scalar(select(RiskFinding).where(RiskFinding.id == finding_id))

    @staticmethod
    def get_by_workspace_id(
        db: Session,
        workspace_id: UUID,
        risk_type: str | None = None,
    ) -> list[RiskFinding]:
        statement = select(RiskFinding).where(RiskFinding.workspace_id == workspace_id)
        if risk_type:
            statement = statement.where(RiskFinding.risk_type == risk_type)

        statement = statement.order_by(RiskFinding.created_at.asc(), RiskFinding.id.asc())
        return list(db.scalars(statement))

    @staticmethod
    def get_by_document_id(db: Session, document_id: UUID) -> list[RiskFinding]:
        statement = (
            select(RiskFinding)
            .where(RiskFinding.document_id == document_id)
            .order_by(RiskFinding.created_at.asc(), RiskFinding.id.asc())
        )
        return list(db.scalars(statement))

    @staticmethod
    def list_by_workspace(
        db: Session,
        workspace_id: UUID,
        *,
        risk_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        limit: int,
        offset: int,
    ) -> list[RiskFinding]:
        statement = select(RiskFinding).where(RiskFinding.workspace_id == workspace_id)
        statement = RiskFindingRepository._apply_filters(
            statement,
            risk_type=risk_type,
            severity=severity,
            status=status,
        )
        statement = statement.order_by(RiskFinding.created_at.desc(), RiskFinding.id.desc())
        statement = statement.limit(limit).offset(offset)
        return list(db.scalars(statement))

    @staticmethod
    def count_by_workspace(
        db: Session,
        workspace_id: UUID,
        *,
        risk_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> int:
        statement = select(func.count(RiskFinding.id)).where(RiskFinding.workspace_id == workspace_id)
        statement = RiskFindingRepository._apply_filters(
            statement,
            risk_type=risk_type,
            severity=severity,
            status=status,
        )
        return int(db.scalar(statement) or 0)

    @staticmethod
    def list_by_document(
        db: Session,
        document_id: UUID,
        *,
        risk_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        limit: int,
        offset: int,
    ) -> list[RiskFinding]:
        statement = select(RiskFinding).where(RiskFinding.document_id == document_id)
        statement = RiskFindingRepository._apply_filters(
            statement,
            risk_type=risk_type,
            severity=severity,
            status=status,
        )
        statement = statement.order_by(RiskFinding.created_at.desc(), RiskFinding.id.desc())
        statement = statement.limit(limit).offset(offset)
        return list(db.scalars(statement))

    @staticmethod
    def count_by_document(
        db: Session,
        document_id: UUID,
        *,
        risk_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> int:
        statement = select(func.count(RiskFinding.id)).where(RiskFinding.document_id == document_id)
        statement = RiskFindingRepository._apply_filters(
            statement,
            risk_type=risk_type,
            severity=severity,
            status=status,
        )
        return int(db.scalar(statement) or 0)

    @staticmethod
    def delete_by_workspace_id(db: Session, workspace_id: UUID) -> int:
        result = db.execute(delete(RiskFinding).where(RiskFinding.workspace_id == workspace_id))
        db.commit()
        return int(result.rowcount or 0)

    @staticmethod
    def get_summary_by_workspace(db: Session, workspace_id: UUID) -> dict:
        total_findings = int(
            db.scalar(
                select(func.count(RiskFinding.id)).where(RiskFinding.workspace_id == workspace_id)
            )
            or 0
        )

        status_rows = db.execute(
            select(RiskFinding.status, func.count(RiskFinding.id))
            .where(RiskFinding.workspace_id == workspace_id)
            .group_by(RiskFinding.status)
        ).all()

        severity_rows = db.execute(
            select(RiskFinding.severity, func.count(RiskFinding.id))
            .where(RiskFinding.workspace_id == workspace_id)
            .group_by(RiskFinding.severity)
        ).all()

        risk_type_rows = db.execute(
            select(RiskFinding.risk_type, func.count(RiskFinding.id))
            .where(RiskFinding.workspace_id == workspace_id)
            .group_by(RiskFinding.risk_type)
        ).all()

        return {
            "workspace_id": workspace_id,
            "total_findings": total_findings,
            "counts_by_status": {status: int(count) for status, count in status_rows},
            "counts_by_severity": {severity: int(count) for severity, count in severity_rows},
            "counts_by_risk_type": {risk_type: int(count) for risk_type, count in risk_type_rows},
        }

    @staticmethod
    def update_status(db: Session, finding: RiskFinding, status: str) -> RiskFinding:
        finding.status = status
        db.commit()
        db.refresh(finding)
        return finding

    @staticmethod
    def _apply_filters(
        statement,
        *,
        risk_type: str | None,
        severity: str | None,
        status: str | None,
    ):
        if risk_type:
            statement = statement.where(RiskFinding.risk_type == risk_type)

        if severity:
            statement = statement.where(RiskFinding.severity == severity)

        if status:
            statement = statement.where(RiskFinding.status == status)

        return statement
