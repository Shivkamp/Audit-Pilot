from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any


def normalize_key(key: Any) -> str:
    normalized = str(key or "").strip().lower()
    normalized = re.sub(r"[\s\-/]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def clean_string(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    if text.lower() in {"nan", "none", "null", "nat"}:
        return None

    return text


def get_value(raw_data: dict[str, Any], aliases: tuple[str, ...] | list[str]) -> Any:
    if not isinstance(raw_data, dict):
        return None

    normalized_lookup: dict[str, Any] = {}
    for key, value in raw_data.items():
        normalized_lookup[normalize_key(key)] = value

    for alias in aliases:
        value = normalized_lookup.get(normalize_key(alias))
        if value is None:
            continue

        if isinstance(value, str):
            cleaned = clean_string(value)
            if cleaned is None:
                continue
            return cleaned

        return value

    return None


def parse_decimal(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        parsed = float(value)
        if math.isfinite(parsed):
            return parsed
        return None

    text = clean_string(value)
    if text is None:
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    text = text.replace(",", "")
    text = text.replace("₹", "")
    text = re.sub(r"(?i)\binr\b", "", text)
    text = re.sub(r"(?i)\brs\.?\b", "", text)
    text = text.replace(" ", "")
    text = re.sub(r"[^0-9.\-]", "", text)

    if text in {"", ".", "-", "-."}:
        return None

    if text.count(".") > 1:
        return None

    try:
        parsed = float(text)
    except ValueError:
        return None

    if not math.isfinite(parsed):
        return None

    if negative and parsed > 0:
        parsed = -parsed

    return parsed


def parse_date(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    text = clean_string(value)
    if text is None:
        return None

    try:
        iso_candidate = text.replace("Z", "+00:00")
        return datetime.fromisoformat(iso_candidate).date().isoformat()
    except ValueError:
        pass

    formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%y",
        "%d-%m-%y",
    )
    for date_format in formats:
        try:
            return datetime.strptime(text, date_format).date().isoformat()
        except ValueError:
            continue

    return None


def parse_month(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.strftime("%Y-%m")

    if isinstance(value, date):
        return value.strftime("%Y-%m")

    text = clean_string(value)
    if text is None:
        return None

    text_lower = text.lower()

    year_month_match = re.fullmatch(r"(\d{4})[-/](\d{1,2})", text_lower)
    if year_month_match:
        year = int(year_month_match.group(1))
        month = int(year_month_match.group(2))
        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}"

    month_year_match = re.fullmatch(r"([a-z]{3,9})[-\s](\d{4})", text_lower)
    if month_year_match:
        month_text = month_year_match.group(1)[:3]
        month_lookup = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        month = month_lookup.get(month_text)
        if month is not None:
            return f"{int(month_year_match.group(2)):04d}-{month:02d}"

    mm_yyyy_match = re.fullmatch(r"(\d{1,2})[-/](\d{4})", text_lower)
    if mm_yyyy_match:
        month = int(mm_yyyy_match.group(1))
        year = int(mm_yyyy_match.group(2))
        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}"

    parsed_date = parse_date(text)
    if parsed_date:
        return parsed_date[:7]

    return None


def parse_rate(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        parsed = float(value)
        if math.isfinite(parsed):
            return parsed
        return None

    text = clean_string(value)
    if text is None:
        return None

    text = text.replace("%", "")
    parsed = parse_decimal(text)
    if parsed is None:
        return None

    return parsed


def build_error(field: str, message: str) -> dict[str, str]:
    return {"field": field, "message": message}


def get_record_value(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def get_record_raw_data(record: Any) -> dict[str, Any]:
    raw_data = get_record_value(record, "raw_data")
    if isinstance(raw_data, dict):
        return raw_data
    return {}


def get_record_raw_text(record: Any) -> str | None:
    return clean_string(get_record_value(record, "raw_text"))