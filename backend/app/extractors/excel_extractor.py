from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from fastapi import status

from app.core.constants import (
    EXTRACTION_FAILED,
    EXTRACTION_RECORD_TYPE_EXCEL_ROW,
    EXTRACTION_TOO_MANY_COLUMNS,
    EXTRACTION_TOO_MANY_ROWS,
    EXTRACTION_TOO_MANY_SHEETS,
)
from app.core.exceptions import AppException
from app.extractors.base import ExtractedItem, clean_cell_value, clean_row_dict, is_empty_row


class ExcelExtractor:
    @staticmethod
    def extract_batches(
        file_path: Path,
        *,
        max_sheets: int,
        max_rows: int,
        max_columns: int,
        batch_size: int,
    ) -> Iterator[list[ExtractedItem]]:
        try:
            import pandas as pd
        except Exception as exc:  # pragma: no cover - dependency/runtime guard
            raise AppException(
                message="Excel extraction dependency is not available.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc

        extension = file_path.suffix.lower()
        engine = "openpyxl" if extension == ".xlsx" else "xlrd"

        try:
            with pd.ExcelFile(file_path, engine=engine) as excel_file:
                sheet_names = list(excel_file.sheet_names)
                if len(sheet_names) > max_sheets:
                    raise AppException(
                        message=(
                            f"Excel file exceeds MVP processing limit of {max_sheets} sheets. "
                            "Please upload a reduced workbook."
                        ),
                        status_code=status.HTTP_400_BAD_REQUEST,
                        error_code=EXTRACTION_TOO_MANY_SHEETS,
                    )

                total_rows = 0
                batch: list[ExtractedItem] = []

                for sheet_name in sheet_names:
                    dataframe = pd.read_excel(
                        excel_file,
                        sheet_name=sheet_name,
                        dtype=str,
                        engine=engine,
                    )

                    if int(dataframe.shape[1]) > max_columns:
                        raise AppException(
                            message=(
                                f"Excel file exceeds MVP processing limit of {max_columns} columns. "
                                "Please reduce column count and re-upload."
                            ),
                            status_code=status.HTTP_400_BAD_REQUEST,
                            error_code=EXTRACTION_TOO_MANY_COLUMNS,
                        )

                    normalized_columns: list[str] = []
                    for index, column_name in enumerate(dataframe.columns, start=1):
                        cleaned_column = clean_cell_value(column_name)
                        column_text = str(cleaned_column).strip() if cleaned_column is not None else ""
                        if not column_text:
                            column_text = f"column_{index}"
                        normalized_columns.append(column_text)

                    dataframe.columns = normalized_columns

                    # Row numbering convention: pandas row index 0 corresponds to
                    # Excel data row 2 when row 1 is treated as the header.
                    for row_index, row_values in enumerate(
                        dataframe.itertuples(index=False, name=None),
                        start=2,
                    ):
                        row_dict = clean_row_dict(dict(zip(dataframe.columns, row_values, strict=True)))
                        if is_empty_row(row_dict):
                            continue

                        total_rows += 1
                        if total_rows > max_rows:
                            raise AppException(
                                message=(
                                    f"Excel file exceeds MVP processing limit of {max_rows} rows. "
                                    "Please upload a filtered file or CSV export."
                                ),
                                status_code=status.HTTP_400_BAD_REQUEST,
                                error_code=EXTRACTION_TOO_MANY_ROWS,
                            )

                        batch.append(
                            ExtractedItem(
                                record_type=EXTRACTION_RECORD_TYPE_EXCEL_ROW,
                                sheet_name=sheet_name,
                                row_number=row_index,
                                raw_data=row_dict,
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
                message="Failed to extract content from Excel file.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=EXTRACTION_FAILED,
            ) from exc
