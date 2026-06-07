from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import tempfile
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    ALLOWED_DOCUMENT_EXTENSIONS,
    DOCUMENT_STATUS_DELETED,
    EXTRACTION_FAILED,
    EXTRACTION_FILE_NOT_FOUND,
    EXTRACTION_FILE_TOO_LARGE,
    EXTRACTION_NO_CONTENT_FOUND,
    EXTRACTION_RECORD_TYPE_CSV_ROW,
    EXTRACTION_RECORD_TYPE_EXCEL_ROW,
    EXTRACTION_RECORD_TYPE_METADATA,
    EXTRACTION_RECORD_TYPE_TABLE_ROW,
    EXTRACTION_RECORD_TYPE_TEXT,
    EXTRACTION_STORAGE_BACKEND_UNSUPPORTED,
    EXTRACTION_UNSUPPORTED_FILE_TYPE,
    JOB_STATUS_EXTRACTING,
    STORAGE_BACKEND_LOCAL,
    STORAGE_BACKEND_S3,
)
from app.core.exceptions import AppException
from app.core.logging import logger
from app.extractors import CSVExtractor, ExcelExtractor, ExtractedItem, PDFExtractor
from app.models.document import Document
from app.models.extracted_record import ExtractedRecord
from app.repositories.document_repository import DocumentRepository
from app.repositories.extraction_repository import ExtractionRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.services.document_service import DocumentService
from app.services.workspace_service import WorkspaceService


class ExtractionService:
    @staticmethod
    def extract_document(
        db: Session,
        document_id: UUID,
        job_id: UUID | None = None,
    ) -> dict:
        document = DocumentRepository.get_by_id(db, document_id)
        if document is None:
            raise AppException(
                message="Document not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="DOCUMENT_NOT_FOUND",
            )

        if document.status == DOCUMENT_STATUS_DELETED:
            raise AppException(
                message="Cannot extract content from a deleted document.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="DOCUMENT_DELETED",
            )

        extension = (document.file_extension or "").lower().strip()
        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise AppException(
                message="Unsupported file type for extraction. Supported types: PDF, XLSX, XLS, CSV.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=EXTRACTION_UNSUPPORTED_FILE_TYPE,
            )

        ExtractionService._validate_file_size(document.file_size_bytes, extension)
        local_file_path, _tmp_path = ExtractionService._resolve_local_file_path(document)

        ExtractionRepository.delete_records_by_document(db, document.id)

        job = ProcessingJobRepository.get_by_id(db, job_id) if job_id is not None else None
        if job is not None:
            ProcessingJobRepository.update_status(
                db,
                job,
                status=JOB_STATUS_EXTRACTING,
                progress_percent=20,
                current_step="Extracting document content",
                error_message=None,
            )

        summary = {
            "document_id": document.id,
            "total_records": 0,
            "text_records": 0,
            "excel_rows": 0,
            "csv_rows": 0,
            "table_rows": 0,
            "metadata_records": 0,
            "pages_detected": set(),
            "sheets_detected": set(),
        }

        batches_processed = 0
        last_progress_percent = 20

        try:
            for batch in ExtractionService._get_extractor_batches(local_file_path, extension):
                if not batch:
                    continue

                db_records: list[ExtractedRecord] = []
                for item in batch:
                    db_records.append(
                        ExtractedRecord(
                            document_id=document.id,
                            workspace_id=document.workspace_id,
                            record_type=item.record_type,
                            page_number=item.page_number,
                            sheet_name=item.sheet_name,
                            row_number=item.row_number,
                            column_name=item.column_name,
                            raw_text=item.raw_text,
                            raw_data=item.raw_data,
                        )
                    )
                    ExtractionService._update_summary_from_item(summary, item)

                inserted_count = ExtractionRepository.bulk_create_records(db, db_records)
                summary["total_records"] += inserted_count
                batches_processed += 1

                if job is not None:
                    progress_percent = ExtractionService._estimate_progress_percent(
                        extension=extension,
                        summary=summary,
                        batches_processed=batches_processed,
                    )
                    if progress_percent > last_progress_percent:
                        ProcessingJobRepository.update_status(
                            db,
                            job,
                            status=JOB_STATUS_EXTRACTING,
                            progress_percent=progress_percent,
                            current_step="Extracting document content",
                            error_message=None,
                        )
                        last_progress_percent = progress_percent
        except AppException:
            raise
        except Exception as exc:
            logger.exception("Unexpected extraction failure for document_id=%s", document.id)
            raise AppException(
                message="Extraction failed due to an internal processing error.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc
        finally:
            if _tmp_path is not None:
                _tmp_path.unlink(missing_ok=True)

        if extension in {".xlsx", ".xls", ".csv"} and summary["total_records"] == 0:
            raise AppException(
                message="No extractable content found in this file.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=EXTRACTION_NO_CONTENT_FOUND,
            )

        if job is not None and last_progress_percent < 95:
            ProcessingJobRepository.update_status(
                db,
                job,
                status=JOB_STATUS_EXTRACTING,
                progress_percent=95,
                current_step="Extraction batches persisted",
                error_message=None,
            )

        return {
            "document_id": summary["document_id"],
            "total_records": summary["total_records"],
            "text_records": summary["text_records"],
            "excel_rows": summary["excel_rows"],
            "csv_rows": summary["csv_rows"],
            "table_rows": summary["table_rows"],
            "metadata_records": summary["metadata_records"],
            "pages_detected": sorted(summary["pages_detected"]),
            "sheets_detected": sorted(summary["sheets_detected"]),
        }

    @staticmethod
    def get_document_extracted_records(
        db: Session,
        document_id: UUID,
        limit: int,
        offset: int,
        record_type: str | None = None,
    ) -> dict:
        document = DocumentService.get_document(db, document_id)

        safe_limit = max(1, min(limit, settings.extraction_api_max_limit))
        safe_offset = max(0, offset)

        records = ExtractionRepository.get_records_by_document(
            db,
            document_id=document.id,
            limit=safe_limit,
            offset=safe_offset,
            record_type=record_type,
        )
        total_records = ExtractionRepository.count_records_by_document(
            db,
            document_id=document.id,
            record_type=record_type,
        )

        return {
            "document_id": document.id,
            "total_records": total_records,
            "limit": safe_limit,
            "offset": safe_offset,
            "records": records,
        }

    @staticmethod
    def get_document_extraction_summary(db: Session, document_id: UUID) -> dict:
        document = DocumentService.get_document(db, document_id)
        raw_summary = ExtractionRepository.get_summary_by_document(db, document.id)
        record_type_counts: dict[str, int] = raw_summary["record_type_counts"]

        return {
            "document_id": document.id,
            "total_records": sum(record_type_counts.values()),
            "text_records": record_type_counts.get(EXTRACTION_RECORD_TYPE_TEXT, 0),
            "excel_rows": record_type_counts.get(EXTRACTION_RECORD_TYPE_EXCEL_ROW, 0),
            "csv_rows": record_type_counts.get(EXTRACTION_RECORD_TYPE_CSV_ROW, 0),
            "table_rows": record_type_counts.get(EXTRACTION_RECORD_TYPE_TABLE_ROW, 0),
            "metadata_records": record_type_counts.get(EXTRACTION_RECORD_TYPE_METADATA, 0),
            "pages_detected": raw_summary["pages_detected"],
            "sheets_detected": raw_summary["sheets_detected"],
        }

    @staticmethod
    def get_workspace_extraction_summary(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        document_summaries = ExtractionRepository.get_workspace_extraction_summary(db, workspace.id)

        return {
            "workspace_id": workspace.id,
            "documents": document_summaries,
        }

    @staticmethod
    def _validate_file_size(file_size_bytes: int, extension: str) -> None:
        max_mb_map = {
            ".pdf": settings.max_pdf_size_mb,
            ".xlsx": settings.max_excel_size_mb,
            ".xls": settings.max_excel_size_mb,
            ".csv": settings.max_csv_size_mb,
        }

        max_file_size_mb = max_mb_map[extension]
        max_file_size_bytes = max_file_size_mb * 1024 * 1024

        if file_size_bytes > max_file_size_bytes:
            if extension == ".pdf":
                file_type = "PDF"
            elif extension in {".xlsx", ".xls"}:
                file_type = "Excel"
            else:
                file_type = "CSV"

            raise AppException(
                message=(
                    f"{file_type} file exceeds extraction limit of {max_file_size_mb} MB. "
                    "Please upload a smaller file."
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=EXTRACTION_FILE_TOO_LARGE,
            )

    @staticmethod
    def _resolve_local_file_path(document: Document) -> tuple[Path, Path | None]:
        if document.storage_backend == STORAGE_BACKEND_S3:
            from app.storage.service import StorageService
            from app.storage.s3 import S3StorageBackend
            storage = StorageService.get_backend(STORAGE_BACKEND_S3)
            assert isinstance(storage, S3StorageBackend)
            suffix = Path(document.stored_filename or document.storage_key).suffix
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.close()
            tmp_path = Path(tmp.name)
            storage.download_to_file(document.storage_key, tmp_path)
            return tmp_path, tmp_path

        if document.storage_backend not in (STORAGE_BACKEND_LOCAL, STORAGE_BACKEND_S3):
            raise AppException(
                message="Unsupported storage backend for extraction.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=EXTRACTION_STORAGE_BACKEND_UNSUPPORTED,
            )

        upload_root = Path(settings.upload_dir).resolve()
        resolved_path = (upload_root / Path(document.storage_key)).resolve()

        try:
            resolved_path.relative_to(upload_root)
        except ValueError as exc:
            raise AppException(
                message="Document file not found for extraction.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=EXTRACTION_FILE_NOT_FOUND,
            ) from exc

        if not resolved_path.exists() or not resolved_path.is_file():
            raise AppException(
                message="Document file not found for extraction.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=EXTRACTION_FILE_NOT_FOUND,
            )

        return resolved_path, None

    @staticmethod
    def _get_extractor_batches(
        local_file_path: Path,
        extension: str,
    ) -> Iterator[list[ExtractedItem]]:
        if extension == ".pdf":
            return PDFExtractor.extract_batches(
                local_file_path,
                max_pages=settings.max_pdf_pages,
                batch_size=settings.extraction_batch_size,
            )

        if extension in {".xlsx", ".xls"}:
            return ExcelExtractor.extract_batches(
                local_file_path,
                max_sheets=settings.max_excel_sheets,
                max_rows=settings.max_excel_rows,
                max_columns=settings.max_columns,
                batch_size=settings.extraction_batch_size,
            )

        if extension == ".csv":
            return CSVExtractor.extract_batches(
                local_file_path,
                max_rows=settings.max_csv_rows,
                max_columns=settings.max_columns,
                batch_size=settings.extraction_batch_size,
            )

        raise AppException(
            message="Unsupported file type for extraction. Supported types: PDF, XLSX, XLS, CSV.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=EXTRACTION_UNSUPPORTED_FILE_TYPE,
        )

    @staticmethod
    def _estimate_progress_percent(
        *,
        extension: str,
        summary: dict,
        batches_processed: int,
    ) -> int:
        if extension == ".pdf":
            ratio = len(summary["pages_detected"]) / max(settings.max_pdf_pages, 1)
        elif extension in {".xlsx", ".xls"}:
            ratio = summary["excel_rows"] / max(settings.max_excel_rows, 1)
        else:
            ratio = summary["csv_rows"] / max(settings.max_csv_rows, 1)

        ratio_progress = 20 + int(min(max(ratio, 0), 1) * 75)
        batch_progress = min(95, 20 + batches_processed * 2)
        return max(20, min(95, max(ratio_progress, batch_progress)))

    @staticmethod
    def _update_summary_from_item(summary: dict, item: ExtractedItem) -> None:
        if item.record_type == EXTRACTION_RECORD_TYPE_TEXT:
            summary["text_records"] += 1
        elif item.record_type == EXTRACTION_RECORD_TYPE_EXCEL_ROW:
            summary["excel_rows"] += 1
        elif item.record_type == EXTRACTION_RECORD_TYPE_CSV_ROW:
            summary["csv_rows"] += 1
        elif item.record_type == EXTRACTION_RECORD_TYPE_TABLE_ROW:
            summary["table_rows"] += 1
        elif item.record_type == EXTRACTION_RECORD_TYPE_METADATA:
            summary["metadata_records"] += 1

        if item.page_number is not None:
            summary["pages_detected"].add(item.page_number)

        if item.sheet_name:
            summary["sheets_detected"].add(item.sheet_name)
