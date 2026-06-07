from __future__ import annotations

import math
import re
from typing import Any

_BLANK_TOKENS = {"", "nan", "null", "none", "na", "n/a"}


def clean_string(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    lowered = text.lower()
    if lowered in _BLANK_TOKENS:
        return None

    return text


def safe_lower(value: Any) -> str | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    return cleaned.lower()


def is_blank(value: Any) -> bool:
    return clean_string(value) is None


def to_decimal(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        numeric = float(value)
        if math.isfinite(numeric):
            return numeric
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
        numeric = float(text)
    except ValueError:
        return None

    if not math.isfinite(numeric):
        return None

    if negative and numeric > 0:
        numeric = -numeric

    return numeric


def make_key(*parts: Any) -> tuple[str, ...]:
    normalized_parts: list[str] = []
    for part in parts:
        decimal_value = to_decimal(part)
        if decimal_value is not None and not isinstance(part, bool):
            normalized_parts.append(f"{decimal_value:.2f}")
            continue

        normalized_parts.append(safe_lower(part) or "")

    return tuple(normalized_parts)


def normalize_vendor_name(value: Any) -> str | None:
    text = safe_lower(value)
    if text is None:
        return None

    text = re.sub(r"\bprivate\b", "pvt", text)
    text = re.sub(r"\bpvt\.?\b", "pvt", text)
    text = re.sub(r"\blimited\b", "ltd", text)
    text = re.sub(r"\bltd\.?\b", "ltd", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return None

    return text
