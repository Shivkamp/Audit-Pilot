from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, distinct, func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.extracted_record import ExtractedRecord


class ExtractionRepository:
    @staticmethod
    def bulk_create_records(db: Session, records: Sequence[ExtractedRecord]) -> int:
        if not records:
            return 0

        db.add_all(records)
        db.commit()
        return len(records)

    @staticmethod
    def get_by_id(db: Session, extracted_record_id: UUID) -> ExtractedRecord | None:
        statement = select(ExtractedRecord).where(ExtractedRecord.id == extracted_record_id)
        return db.scalar(statement)

    @staticmethod
    def get_records_by_document(
        db: Session,
        document_id: UUID,
        limit: int,
        offset: int,
        record_type: str | None = None,
    ) -> list[ExtractedRecord]:
        statement = select(ExtractedRecord).where(ExtractedRecord.document_id == document_id)

        if record_type:
            statement = statement.where(ExtractedRecord.record_type == record_type)

        statement = statement.order_by(ExtractedRecord.created_at.asc(), ExtractedRecord.id.asc())
        statement = statement.limit(limit).offset(offset)
        return list(db.scalars(statement))

    @staticmethod
    def count_records_by_document(
        db: Session,
        document_id: UUID,
        record_type: str | None = None,
    ) -> int:
        statement = select(func.count(ExtractedRecord.id)).where(
            ExtractedRecord.document_id == document_id
        )
        if record_type:
            statement = statement.where(ExtractedRecord.record_type == record_type)

        return int(db.scalar(statement) or 0)

    @staticmethod
    def has_extracted_records(db: Session, document_id: UUID) -> bool:
        statement = (
            select(ExtractedRecord.id)
            .where(ExtractedRecord.document_id == document_id)
            .limit(1)
        )
        return db.scalar(statement) is not None

    @staticmethod
    def get_classification_sample_records(
        db: Session,
        document_id: UUID,
        limit: int,
    ) -> list[ExtractedRecord]:
        if limit <= 0:
            return []

        statement = (
            select(ExtractedRecord)
            .where(ExtractedRecord.document_id == document_id)
            .order_by(ExtractedRecord.created_at.asc(), ExtractedRecord.id.asc())
            .limit(limit)
        )
        return list(db.scalars(statement))

    @staticmethod
    def get_distinct_sheet_names_for_document(db: Session, document_id: UUID) -> list[str]:
        statement = (
            select(distinct(ExtractedRecord.sheet_name))
            .where(ExtractedRecord.document_id == document_id)
            .where(ExtractedRecord.sheet_name.is_not(None))
            .order_by(ExtractedRecord.sheet_name.asc())
        )
        return [str(sheet) for sheet in db.scalars(statement) if sheet]

    @staticmethod
    def delete_records_by_document(db: Session, document_id: UUID) -> int:
        result = db.execute(
            delete(ExtractedRecord).where(ExtractedRecord.document_id == document_id)
        )
        db.commit()
        return int(result.rowcount or 0)

    @staticmethod
    def get_summary_by_document(db: Session, document_id: UUID) -> dict:
        counts_statement = (
            select(ExtractedRecord.record_type, func.count(ExtractedRecord.id))
            .where(ExtractedRecord.document_id == document_id)
            .group_by(ExtractedRecord.record_type)
        )
        count_rows = db.execute(counts_statement).all()

        pages = list(
            db.scalars(
                select(distinct(ExtractedRecord.page_number))
                .where(ExtractedRecord.document_id == document_id)
                .where(ExtractedRecord.page_number.is_not(None))
                .order_by(ExtractedRecord.page_number.asc())
            )
        )

        sheets = list(
            db.scalars(
                select(distinct(ExtractedRecord.sheet_name))
                .where(ExtractedRecord.document_id == document_id)
                .where(ExtractedRecord.sheet_name.is_not(None))
                .order_by(ExtractedRecord.sheet_name.asc())
            )
        )

        return {
            "record_type_counts": {record_type: int(count) for record_type, count in count_rows},
            "pages_detected": [int(page) for page in pages],
            "sheets_detected": [str(sheet) for sheet in sheets],
        }

    @staticmethod
    def get_workspace_extraction_summary(db: Session, workspace_id: UUID) -> list[dict]:
        documents = db.execute(
            select(Document.id, Document.original_filename, Document.status)
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
        ).all()

        counts_rows = db.execute(
            select(
                ExtractedRecord.document_id,
                ExtractedRecord.record_type,
                func.count(ExtractedRecord.id),
            )
            .where(ExtractedRecord.workspace_id == workspace_id)
            .group_by(ExtractedRecord.document_id, ExtractedRecord.record_type)
        ).all()

        summary_by_document: dict[UUID, dict] = {
            document_id: {
                "document_id": document_id,
                "original_filename": original_filename,
                "document_status": document_status,
                "total_extracted_records": 0,
                "text_records": 0,
                "excel_rows": 0,
                "csv_rows": 0,
                "table_rows": 0,
                "metadata_records": 0,
            }
            for document_id, original_filename, document_status in documents
        }

        for document_id, record_type, count in counts_rows:
            if document_id not in summary_by_document:
                continue

            count_value = int(count)
            doc_summary = summary_by_document[document_id]
            doc_summary["total_extracted_records"] += count_value

            if record_type == "text":
                doc_summary["text_records"] += count_value
            elif record_type == "excel_row":
                doc_summary["excel_rows"] += count_value
            elif record_type == "csv_row":
                doc_summary["csv_rows"] += count_value
            elif record_type == "table_row":
                doc_summary["table_rows"] += count_value
            elif record_type == "metadata":
                doc_summary["metadata_records"] += count_value

        return [summary_by_document[document_id] for document_id, _, _ in documents]
