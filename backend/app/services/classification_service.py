from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.classifiers import ClassificationEvidence, DocumentClassifier
from app.core.config import settings
from app.core.constants import (
    CLASSIFICATION_DOCUMENT_DELETED,
    CLASSIFICATION_DOCUMENT_NOT_FOUND,
    CLASSIFICATION_FAILED,
    CLASSIFICATION_REQUIRES_EXTRACTION,
    DOCUMENT_STATUS_DELETED,
    DOCUMENT_TYPE_UNKNOWN,
)
from app.core.exceptions import AppException
from app.models.document import Document
from app.models.extracted_record import ExtractedRecord
from app.repositories.document_repository import DocumentRepository
from app.repositories.extraction_repository import ExtractionRepository
from app.services.workspace_service import WorkspaceService


class ClassificationService:
    @staticmethod
    def classify_document(db: Session, document_id: UUID) -> dict:
        try:
            document = ClassificationService._get_document_or_raise(db, document_id)

            if not ExtractionRepository.has_extracted_records(db, document.id):
                raise AppException(
                    message="Document extraction data is required before classification.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=CLASSIFICATION_REQUIRES_EXTRACTION,
                )

            sample_limit = max(1, settings.classification_sample_record_limit)
            sample_records = ExtractionRepository.get_classification_sample_records(
                db,
                document.id,
                sample_limit,
            )
            sheet_names = ExtractionRepository.get_distinct_sheet_names_for_document(
                db,
                document.id,
            )
            column_names, sample_raw_data, sample_text = ClassificationService._build_evidence_parts(
                sample_records
            )

            classifier = DocumentClassifier(
                min_confidence=settings.classification_min_confidence,
                ambiguity_margin=settings.classification_ambiguity_margin,
            )
            result = classifier.classify(
                ClassificationEvidence(
                    original_filename=document.original_filename,
                    file_extension=document.file_extension,
                    content_type=document.content_type,
                    sheet_names=sheet_names,
                    column_names=column_names,
                    sample_text=sample_text,
                    sample_raw_data=sample_raw_data,
                )
            )

            updated_document = DocumentRepository.update_classification(
                db,
                document,
                document_type=result.document_type,
                classification_confidence=result.confidence,
                classification_method=result.method,
                classification_reason=result.reason,
                classified_at=datetime.now(timezone.utc),
            )

            return ClassificationService._serialize_document_classification(updated_document)
        except AppException:
            raise
        except Exception as exc:
            raise AppException(
                message="Classification failed due to an internal processing error.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=CLASSIFICATION_FAILED,
            ) from exc

    @staticmethod
    def get_document_classification(db: Session, document_id: UUID) -> dict:
        document = ClassificationService._get_document_or_raise(db, document_id)
        return ClassificationService._serialize_document_classification(document)

    @staticmethod
    def get_workspace_classification_summary(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        documents = DocumentRepository.get_workspace_documents_with_classification(
            db,
            workspace.id,
            include_deleted=False,
        )

        counts_by_document_type: dict[str, int] = {}
        serialized_documents: list[dict] = []

        for document in documents:
            document_type = document.document_type or DOCUMENT_TYPE_UNKNOWN
            counts_by_document_type[document_type] = counts_by_document_type.get(document_type, 0) + 1
            serialized_documents.append(
                {
                    "document_id": document.id,
                    "original_filename": document.original_filename,
                    "status": document.status,
                    "document_type": document_type,
                    "classification_confidence": document.classification_confidence,
                    "classified_at": document.classified_at,
                }
            )

        return {
            "workspace_id": workspace.id,
            "documents": serialized_documents,
            "counts_by_document_type": counts_by_document_type,
        }

    @staticmethod
    def _get_document_or_raise(db: Session, document_id: UUID) -> Document:
        document = DocumentRepository.get_document_by_id(db, document_id)
        if document is None:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=CLASSIFICATION_DOCUMENT_NOT_FOUND,
            )

        if document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Cannot classify a deleted document.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=CLASSIFICATION_DOCUMENT_DELETED,
            )

        return document

    @staticmethod
    def _serialize_document_classification(document: Document) -> dict:
        return {
            "document_id": document.id,
            "original_filename": document.original_filename,
            "status": document.status,
            "document_type": document.document_type or DOCUMENT_TYPE_UNKNOWN,
            "classification_confidence": document.classification_confidence,
            "classification_method": document.classification_method,
            "classification_reason": document.classification_reason,
            "classified_at": document.classified_at,
        }

    @staticmethod
    def _build_evidence_parts(
        sample_records: list[ExtractedRecord],
    ) -> tuple[list[str], list[dict], str]:
        columns: set[str] = set()
        sample_raw_data: list[dict] = []

        remaining_chars = max(0, settings.classification_text_char_limit)
        sample_text_parts: list[str] = []

        for record in sample_records:
            if record.column_name:
                columns.add(record.column_name)

            if isinstance(record.raw_data, dict):
                sample_raw_data.append(record.raw_data)
                columns.update(str(key) for key in record.raw_data.keys())

            if remaining_chars <= 0:
                continue

            raw_text = (record.raw_text or "").strip()
            if not raw_text:
                continue

            text_piece = raw_text[:remaining_chars]
            sample_text_parts.append(text_piece)
            remaining_chars -= len(text_piece)

        sample_text = "\n".join(sample_text_parts)
        return sorted(columns), sample_raw_data, sample_text
