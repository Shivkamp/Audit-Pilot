from __future__ import annotations

from datetime import date, datetime
import logging
import math
from typing import Any
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger("taxaudit_ai")
from app.core.constants import (
    DOCUMENT_STATUS_DELETED,
    DOCUMENT_TYPE_UNKNOWN,
    NORMALIZATION_DOCUMENT_DELETED,
    NORMALIZATION_DOCUMENT_NOT_FOUND,
    NORMALIZATION_FAILED,
    NORMALIZATION_NO_RECORDS_CREATED,
    NORMALIZATION_REQUIRES_CLASSIFICATION,
    NORMALIZATION_REQUIRES_EXTRACTION,
    NORMALIZATION_STATUS_FAILED,
    NORMALIZATION_STATUS_NORMALIZED,
    NORMALIZATION_STATUS_PARTIAL,
    NORMALIZATION_STATUS_SKIPPED,
    NORMALIZATION_UNSUPPORTED_DOCUMENT_TYPE,
)
from app.core.exceptions import AppException
from app.models.document import Document
from app.models.normalized_record import NormalizedRecord
from app.normalizers import get_normalizer_for_document_type
from app.normalizers.base import NormalizedItem
from app.normalizers.common import build_error, clean_string
from app.repositories.document_repository import DocumentRepository
from app.repositories.extraction_repository import ExtractionRepository
from app.repositories.normalization_repository import NormalizationRepository
from app.services.workspace_service import WorkspaceService

_ALLOWED_NORMALIZATION_STATUSES = {
    NORMALIZATION_STATUS_NORMALIZED,
    NORMALIZATION_STATUS_PARTIAL,
    NORMALIZATION_STATUS_FAILED,
    NORMALIZATION_STATUS_SKIPPED,
}


class NormalizationService:
    @staticmethod
    def normalize_document(db: Session, document_id: UUID) -> dict:
        try:
            document = NormalizationService._get_document_or_raise(db, document_id)

            if not document.document_type or document.document_type == DOCUMENT_TYPE_UNKNOWN:
                raise AppException(
                    message="Document classification is required before normalization.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=NORMALIZATION_REQUIRES_CLASSIFICATION,
                )

            normalizer = get_normalizer_for_document_type(document.document_type)
            if normalizer is None:
                raise AppException(
                    message="Normalization is not supported for this document type.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=NORMALIZATION_UNSUPPORTED_DOCUMENT_TYPE,
                )

            if not ExtractionRepository.has_extracted_records(db, document.id):
                raise AppException(
                    message="Document extraction data is required before normalization.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=NORMALIZATION_REQUIRES_EXTRACTION,
                )

            NormalizationRepository.delete_records_by_document(db, document.id)

            batch_size = max(1, settings.normalization_batch_size)
            offset = 0

            counts = {
                NORMALIZATION_STATUS_NORMALIZED: 0,
                NORMALIZATION_STATUS_PARTIAL: 0,
                NORMALIZATION_STATUS_FAILED: 0,
                NORMALIZATION_STATUS_SKIPPED: 0,
            }
            total_processed = 0

            while True:
                extracted_batch = ExtractionRepository.get_records_by_document(
                    db,
                    document_id=document.id,
                    limit=batch_size,
                    offset=offset,
                    record_type=None,
                )
                if not extracted_batch:
                    break

                records_to_insert: list[NormalizedRecord] = []
                for extracted_record in extracted_batch:
                    normalized_item = NormalizationService._normalize_record_safe(
                        normalizer=normalizer,
                        extracted_record=extracted_record,
                        fallback_category=document.document_type,
                    )

                    status_value = normalized_item.normalization_status
                    if status_value not in _ALLOWED_NORMALIZATION_STATUSES:
                        status_value = NORMALIZATION_STATUS_FAILED

                    normalization_errors = NormalizationService._sanitize_errors(
                        normalized_item.normalization_errors
                    )
                    normalized_data = NormalizationService._to_json_safe(
                        normalized_item.normalized_data
                    )
                    if not isinstance(normalized_data, dict):
                        normalized_data = {}

                    source_record_id = normalized_item.source_record_id or extracted_record.id

                    records_to_insert.append(
                        NormalizedRecord(
                            workspace_id=document.workspace_id,
                            document_id=document.id,
                            source_record_id=source_record_id,
                            record_category=normalized_item.record_category,
                            normalized_data=normalized_data,
                            normalization_status=status_value,
                            normalization_confidence=normalized_item.normalization_confidence,
                            normalization_errors=normalization_errors,
                        )
                    )
                    counts[status_value] += 1

                inserted = NormalizationRepository.bulk_create_records(db, records_to_insert)
                total_processed += inserted
                offset += len(extracted_batch)

            if total_processed == 0:
                raise AppException(
                    message="No normalized records were created for this document.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=NORMALIZATION_NO_RECORDS_CREATED,
                )

            return {
                "document_id": document.id,
                "document_type": document.document_type,
                "total_processed": total_processed,
                "normalized": counts[NORMALIZATION_STATUS_NORMALIZED],
                "partial": counts[NORMALIZATION_STATUS_PARTIAL],
                "failed": counts[NORMALIZATION_STATUS_FAILED],
                "skipped": counts[NORMALIZATION_STATUS_SKIPPED],
            }
        except AppException:
            raise
        except Exception as exc:
            raise AppException(
                message="Normalization failed due to an internal processing error.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=NORMALIZATION_FAILED,
            ) from exc

    @staticmethod
    def get_document_normalized_records(
        db: Session,
        document_id: UUID,
        limit: int,
        offset: int,
        record_category: str | None = None,
        normalization_status: str | None = None,
    ) -> dict:
        document = NormalizationService._get_document_or_raise(db, document_id)

        safe_limit = max(1, min(limit, settings.normalization_api_max_limit))
        safe_offset = max(0, offset)

        records = NormalizationRepository.get_records_by_document(
            db,
            document_id=document.id,
            limit=safe_limit,
            offset=safe_offset,
            record_category=record_category,
            normalization_status=normalization_status,
        )
        total_records = NormalizationRepository.count_records_by_document(
            db,
            document_id=document.id,
            record_category=record_category,
            normalization_status=normalization_status,
        )

        return {
            "document_id": document.id,
            "total_records": total_records,
            "limit": safe_limit,
            "offset": safe_offset,
            "records": records,
        }

    @staticmethod
    def get_document_normalization_summary(db: Session, document_id: UUID) -> dict:
        document = NormalizationService._get_document_or_raise(db, document_id)
        raw_summary = NormalizationRepository.get_summary_by_document(db, document.id)
        counts = raw_summary["counts_by_status"]

        return {
            "document_id": document.id,
            "document_type": document.document_type,
            "total_records": int(sum(counts.values())),
            "normalized": int(counts.get(NORMALIZATION_STATUS_NORMALIZED, 0)),
            "partial": int(counts.get(NORMALIZATION_STATUS_PARTIAL, 0)),
            "failed": int(counts.get(NORMALIZATION_STATUS_FAILED, 0)),
            "skipped": int(counts.get(NORMALIZATION_STATUS_SKIPPED, 0)),
        }

    @staticmethod
    def get_workspace_normalization_summary(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        document_summaries = NormalizationRepository.get_workspace_normalization_summary(
            db,
            workspace.id,
        )
        return {
            "workspace_id": workspace.id,
            "documents": document_summaries,
        }

    @staticmethod
    def _get_document_or_raise(db: Session, document_id: UUID) -> Document:
        document = DocumentRepository.get_by_id(db, document_id)
        if document is None:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=NORMALIZATION_DOCUMENT_NOT_FOUND,
            )

        if document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Cannot normalize a deleted document.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=NORMALIZATION_DOCUMENT_DELETED,
            )

        return document

    @staticmethod
    def _normalize_record_safe(
        *,
        normalizer,
        extracted_record,
        fallback_category: str,
    ) -> NormalizedItem:
        try:
            return normalizer.normalize_record(extracted_record)
        except Exception:
            logger.warning(
                "Row normalization failed for extracted_record_id=%s",
                getattr(extracted_record, "id", "unknown"),
                exc_info=True,
            )
            return NormalizedItem(
                source_record_id=getattr(extracted_record, "id", None),
                record_category=fallback_category,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_FAILED,
                normalization_confidence=0.0,
                normalization_errors=[
                    build_error(
                        "record",
                        "Row normalization failed for this extracted record.",
                    )
                ],
            )

    @staticmethod
    def _sanitize_errors(errors: Any) -> list[dict[str, str]] | None:
        if not errors:
            return None

        max_samples = max(1, settings.normalization_max_error_samples)

        if not isinstance(errors, list):
            message = clean_string(errors) or "Normalization issue"
            return [build_error("record", message)]

        sanitized: list[dict[str, str]] = []
        for item in errors:
            if len(sanitized) >= max_samples:
                break

            if isinstance(item, dict):
                field = clean_string(item.get("field")) or "record"
                message = clean_string(item.get("message")) or "Normalization issue"
                sanitized.append(build_error(field, message))
                continue

            sanitized.append(build_error("record", clean_string(item) or "Normalization issue"))

        return sanitized or None

    @staticmethod
    def _to_json_safe(value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, (str, bool, int)):
            return value

        if isinstance(value, float):
            if math.isfinite(value):
                return value
            return None

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if hasattr(value, "item"):
            try:
                return NormalizationService._to_json_safe(value.item())
            except Exception:
                return None

        if isinstance(value, dict):
            return {
                str(key): NormalizationService._to_json_safe(inner_value)
                for key, inner_value in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [NormalizationService._to_json_safe(inner_value) for inner_value in value]

        return clean_string(value)