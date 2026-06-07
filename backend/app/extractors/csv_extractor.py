from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from fastapi import status

from app.core.constants import (
    EXTRACTION_FAILED,
    EXTRACTION_RECORD_TYPE_CSV_ROW,
    EXTRACTION_TOO_MANY_COLUMNS,
    EXTRACTION_TOO_MANY_ROWS,
)
from app.core.exceptions import AppException
from app.extractors.base import ExtractedItem, clean_cell_value, clean_row_dict, is_empty_row


class CSVExtractor:
    @staticmethod
    def extract_batches(
        file_path: Path,
        *,
        max_rows: int,
        max_columns: int,
        batch_size: int,
    ) -> Iterator[list[ExtractedItem]]:
        try:
            import pandas as pd
        except Exception as exc:  # pragma: no cover - dependency/runtime guard
            raise AppException(
                message="CSV extraction dependency is not available.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc

        encoding = CSVExtractor._detect_encoding(file_path)

        try:
            yield from CSVExtractor._extract_with_encoding(
                pd,
                file_path,
                encoding=encoding,
                max_rows=max_rows,
                max_columns=max_columns,
                batch_size=batch_size,
            )
        except AppException:
            raise
        except Exception as exc:
            raise AppException(
                message="Failed to extract content from CSV file.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc

    @staticmethod
    def _detect_encoding(file_path: Path) -> str:
        """Detect file encoding by attempting a full UTF-8 read. Falls back to latin1."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                while f.read(65536):
                    pass
            return "utf-8"
        except UnicodeDecodeError:
            return "latin1"

    @staticmethod
    def _extract_with_encoding(
        pd,
        file_path: Path,
        *,
        encoding: str,
        max_rows: int,
        max_columns: int,
        batch_size: int,
    ) -> Iterator[list[ExtractedItem]]:
        total_non_empty_rows = 0
        source_data_row_counter = 0
        batch: list[ExtractedItem] = []

        with pd.read_csv(
            file_path,
            dtype=str,
            chunksize=batch_size,
            encoding=encoding,
        ) as chunk_iterator:
            for chunk in chunk_iterator:
                if int(chunk.shape[1]) > max_columns:
                    raise AppException(
                        message=(
                            f"CSV file exceeds MVP processing limit of {max_columns} columns. "
                            "Please reduce column count and re-upload."
                        ),
                        status_code=status.HTTP_400_BAD_REQUEST,
                        error_code=EXTRACTION_TOO_MANY_COLUMNS,
                    )

                normalized_columns: list[str] = []
                for index, column_name in enumerate(chunk.columns, start=1):
                    cleaned_column = clean_cell_value(column_name)
                    column_text = str(cleaned_column).strip() if cleaned_column is not None else ""
                    if not column_text:
                        column_text = f"column_{index}"
                    normalized_columns.append(column_text)

                chunk.columns = normalized_columns

                for row_values in chunk.itertuples(index=False, name=None):
                    source_data_row_counter += 1
                    source_row_number = source_data_row_counter + 1  # +1 for CSV header row

                    row_dict = clean_row_dict(dict(zip(chunk.columns, row_values, strict=True)))
                    if is_empty_row(row_dict):
                        continue

                    total_non_empty_rows += 1
                    if total_non_empty_rows > max_rows:
                        raise AppException(
                            message=(
                                f"CSV file exceeds MVP processing limit of {max_rows} rows. "
                                "Please upload a filtered CSV file."
                            ),
                            status_code=status.HTTP_400_BAD_REQUEST,
                            error_code=EXTRACTION_TOO_MANY_ROWS,
                        )

                    batch.append(
                        ExtractedItem(
                            record_type=EXTRACTION_RECORD_TYPE_CSV_ROW,
                            row_number=source_row_number,
                            raw_data=row_dict,
                        )
                    )

                    if len(batch) >= batch_size:
                        yield batch
                        batch = []

        if batch:
            yield batch
