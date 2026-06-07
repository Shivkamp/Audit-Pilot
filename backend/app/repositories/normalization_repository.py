from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.normalized_record import NormalizedRecord


class NormalizationRepository:
    @staticmethod
    def bulk_create_records(db: Session, records: Sequence[NormalizedRecord]) -> int:
        if not records:
            return 0

        db.add_all(records)
        db.commit()
        return len(records)

    @staticmethod
    def delete_records_by_document(db: Session, document_id: UUID) -> int:
        result = db.execute(
            delete(NormalizedRecord).where(NormalizedRecord.document_id == document_id)
        )
        db.commit()
        return int(result.rowcount or 0)

    @staticmethod
    def get_records_by_document(
        db: Session,
        document_id: UUID,
        limit: int,
        offset: int,
        record_category: str | None = None,
        normalization_status: str | None = None,
    ) -> list[NormalizedRecord]:
        statement = select(NormalizedRecord).where(NormalizedRecord.document_id == document_id)

        if record_category:
            statement = statement.where(NormalizedRecord.record_category == record_category)

        if normalization_status:
            statement = statement.where(NormalizedRecord.normalization_status == normalization_status)

        statement = statement.order_by(NormalizedRecord.created_at.asc(), NormalizedRecord.id.asc())
        statement = statement.limit(limit).offset(offset)
        return list(db.scalars(statement))

    @staticmethod
    def get_by_workspace_id(
        db: Session,
        workspace_id: UUID,
        record_category: str | None = None,
    ) -> list[NormalizedRecord]:
        statement = select(NormalizedRecord).where(NormalizedRecord.workspace_id == workspace_id)

        if record_category:
            statement = statement.where(NormalizedRecord.record_category == record_category)

        statement = statement.order_by(NormalizedRecord.created_at.asc(), NormalizedRecord.id.asc())
        return list(db.scalars(statement))

    @staticmethod
    def get_all_by_document_id(db: Session, document_id: UUID) -> list[NormalizedRecord]:
        statement = (
            select(NormalizedRecord)
            .where(NormalizedRecord.document_id == document_id)
            .order_by(NormalizedRecord.created_at.asc(), NormalizedRecord.id.asc())
        )
        return list(db.scalars(statement))

    @staticmethod
    def count_records_by_document(
        db: Session,
        document_id: UUID,
        record_category: str | None = None,
        normalization_status: str | None = None,
    ) -> int:
        statement = select(func.count(NormalizedRecord.id)).where(
            NormalizedRecord.document_id == document_id
        )

        if record_category:
            statement = statement.where(NormalizedRecord.record_category == record_category)

        if normalization_status:
            statement = statement.where(NormalizedRecord.normalization_status == normalization_status)

        return int(db.scalar(statement) or 0)

    @staticmethod
    def get_summary_by_document(db: Session, document_id: UUID) -> dict[str, dict[str, int]]:
        rows = db.execute(
            select(NormalizedRecord.normalization_status, func.count(NormalizedRecord.id))
            .where(NormalizedRecord.document_id == document_id)
            .group_by(NormalizedRecord.normalization_status)
        ).all()

        return {
            "counts_by_status": {status: int(count) for status, count in rows},
        }

    @staticmethod
    def get_workspace_normalization_summary(db: Session, workspace_id: UUID) -> list[dict]:
        documents = db.execute(
            select(
                Document.id,
                Document.original_filename,
                Document.status,
                Document.document_type,
            )
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
        ).all()

        counts_rows = db.execute(
            select(
                NormalizedRecord.document_id,
                NormalizedRecord.normalization_status,
                func.count(NormalizedRecord.id),
            )
            .where(NormalizedRecord.workspace_id == workspace_id)
            .group_by(NormalizedRecord.document_id, NormalizedRecord.normalization_status)
        ).all()

        summary_by_document: dict[UUID, dict] = {
            document_id: {
                "document_id": document_id,
                "original_filename": original_filename,
                "document_status": document_status,
                "document_type": document_type,
                "total_records": 0,
                "normalized": 0,
                "partial": 0,
                "failed": 0,
                "skipped": 0,
            }
            for document_id, original_filename, document_status, document_type in documents
        }

        for document_id, status, count in counts_rows:
            if document_id not in summary_by_document:
                continue

            count_value = int(count)
            doc_summary = summary_by_document[document_id]
            doc_summary[status] = doc_summary.get(status, 0) + count_value
            doc_summary["total_records"] += count_value

        return [
            summary_by_document[document_id]
            for document_id, _, _, _ in documents
        ]