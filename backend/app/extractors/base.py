from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
import math
from typing import Any


@dataclass(slots=True)
class ExtractedItem:
    record_type: str
    page_number: int | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    column_name: str | None = None
    raw_text: str | None = None
    raw_data: dict[str, Any] | None = None


def clean_cell_value(value: Any) -> Any:
    if value is None:
        return None

    # Convert pandas / numpy scalar wrappers into native Python values.
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except Exception:
        pass

    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value

    if isinstance(value, (str, int, bool)):
        return value

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): clean_cell_value(inner_value)
            for key, inner_value in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [clean_cell_value(item) for item in value]

    return str(value)


def clean_row_dict(row_dict: dict[Any, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row_dict.items():
        key_text = str(key).strip() if key is not None else ""
        if not key_text:
            continue
        cleaned[key_text] = clean_cell_value(value)
    return cleaned


def is_empty_row(row_dict: dict[str, Any]) -> bool:
    if not row_dict:
        return True

    for value in row_dict.values():
        if value is None:
            continue

        if isinstance(value, str) and not value.strip():
            continue

        return False

    return True
