from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from fastapi import status

from app.core.constants import (
    EXTRACTION_FAILED,
    EXTRACTION_RECORD_TYPE_METADATA,
    EXTRACTION_RECORD_TYPE_TEXT,
    EXTRACTION_TOO_MANY_PAGES,
)
from app.core.exceptions import AppException
from app.extractors.base import ExtractedItem


class PDFExtractor:
    @staticmethod
    def extract_batches(
        file_path: Path,
        *,
        max_pages: int,
        batch_size: int,
    ) -> Iterator[list[ExtractedItem]]:
        try:
            import fitz
        except Exception as exc:  # pragma: no cover - dependency/runtime guard
            raise AppException(
                message="PDF extraction dependency is not available.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc

        try:
            with fitz.open(str(file_path)) as pdf_document:
                page_count = int(pdf_document.page_count)
                if page_count > max_pages:
                    raise AppException(
                        message=(
                            f"PDF exceeds MVP processing limit of {max_pages} pages. "
                            "Please upload a smaller file."
                        ),
                        status_code=status.HTTP_400_BAD_REQUEST,
                        error_code=EXTRACTION_TOO_MANY_PAGES,
                    )

                batch: list[ExtractedItem] = []
                for page_index in range(page_count):
                    page_number = page_index + 1
                    page = pdf_document.load_page(page_index)
                    page_text = (page.get_text("text") or "").strip()

                    if page_text:
                        batch.append(
                            ExtractedItem(
                                record_type=EXTRACTION_RECORD_TYPE_TEXT,
                                page_number=page_number,
                                raw_text=page_text,
                            )
                        )
                    else:
                        batch.append(
                            ExtractedItem(
                                record_type=EXTRACTION_RECORD_TYPE_METADATA,
                                page_number=page_number,
                                raw_data={"message": "No extractable text found on page"},
                            )
                        )

                    if len(batch) >= batch_size:
                        yield batch
                        batch = []

                if batch:
                    yield batch
        except AppException:
            raise
        except Exception as exc:
            raise AppException(
                message="Failed to extract content from PDF.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc
