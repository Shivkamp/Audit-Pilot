from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from app.retrieval.types import CandidateResult, build_candidate_result

_TDS_SECTION_PATTERN = re.compile(r"\b19[4-9][A-Z]?\b", re.IGNORECASE)
_MONTH_PATTERN = re.compile(r"\b(20[0-9]{2})-(0[1-9]|1[0-2])\b")
_MONTH_NAME_PATTERN = re.compile(
    r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b(?:[\s,\-/]+(20[0-9]{2}))?",
    re.IGNORECASE,
)

_PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
_TAN_PATTERN = re.compile(r"\b[A-Z]{4}[0-9]{5}[A-Z]\b", re.IGNORECASE)
_GSTIN_PATTERN = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]\b", re.IGNORECASE)
_VENDOR_CODE_PATTERN = re.compile(r"\bV[0-9]{3,}\b", re.IGNORECASE)
_INVOICE_PATTERN = re.compile(r"\b(?:invoice|inv)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\-/]{3,})\b", re.IGNORECASE)
_CHALLAN_PATTERN = re.compile(r"\b(?:challan|cin)\s*(?:serial|no|number|#)?\s*[:\-]?\s*([A-Z0-9\-/]{3,})\b", re.IGNORECASE)
_BSR_PATTERN = re.compile(r"\b[0-9]{7}\b")
_AMOUNT_PATTERN = re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b")
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_./-]+")

_MONTH_NAME_MAP = {
    "jan": "01",
    "january": "01",
    "feb": "02",
    "february": "02",
    "mar": "03",
    "march": "03",
    "apr": "04",
    "april": "04",
    "may": "05",
    "jun": "06",
    "june": "06",
    "jul": "07",
    "july": "07",
    "aug": "08",
    "august": "08",
    "sep": "09",
    "sept": "09",
    "september": "09",
    "oct": "10",
    "october": "10",
    "nov": "11",
    "november": "11",
    "dec": "12",
    "december": "12",
}

_RISK_TYPE_PHRASE_MAP = {
    "missing pan": "missing_pan",
    "duplicate invoice": "duplicate_invoice",
    "tds mismatch": "tds_mismatch",
    "short deduction": "tds_mismatch",
    "short deposit": "short_deposit",
    "vendor name mismatch": "vendor_name_mismatch",
    "high value": "high_value_transaction",
}

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "missing",
    "of",
    "on",
    "or",
    "risk",
    "show",
    "short",
    "the",
    "to",
    "was",
    "what",
    "which",
    "why",
    "with",
}


@dataclass
class QuerySignals:
    query_text: str
    query_tokens: set[str] = field(default_factory=set)
    risk_types: set[str] = field(default_factory=set)
    tds_sections: set[str] = field(default_factory=set)
    months: set[str] = field(default_factory=set)
    month_numbers: set[str] = field(default_factory=set)
    pan_values: set[str] = field(default_factory=set)
    tan_values: set[str] = field(default_factory=set)
    gstin_values: set[str] = field(default_factory=set)
    vendor_codes: set[str] = field(default_factory=set)
    invoice_numbers: set[str] = field(default_factory=set)
    challan_serial_numbers: set[str] = field(default_factory=set)
    bsr_codes: set[str] = field(default_factory=set)
    amounts: set[str] = field(default_factory=set)
    vendor_name_terms: set[str] = field(default_factory=set)



def extract_query_signals(query: str, *, explicit_risk_type: str | None = None) -> QuerySignals:
    clean_query = (query or "").strip()
    lowered_query = clean_query.lower()

    signals = QuerySignals(
        query_text=lowered_query,
        query_tokens=set(_tokenize(lowered_query)),
    )

    if explicit_risk_type:
        signals.risk_types.add(explicit_risk_type.strip().lower())

    for phrase, risk_type in _RISK_TYPE_PHRASE_MAP.items():
        if phrase in lowered_query:
            signals.risk_types.add(risk_type)

    signals.tds_sections = {value.lower() for value in _TDS_SECTION_PATTERN.findall(clean_query)}
    signals.pan_values = {value.lower() for value in _PAN_PATTERN.findall(clean_query)}
    signals.tan_values = {value.lower() for value in _TAN_PATTERN.findall(clean_query)}
    signals.gstin_values = {value.lower() for value in _GSTIN_PATTERN.findall(clean_query)}
    signals.vendor_codes = {value.lower() for value in _VENDOR_CODE_PATTERN.findall(clean_query)}
    signals.bsr_codes = {value.lower() for value in _BSR_PATTERN.findall(clean_query)}

    for year, month in _MONTH_PATTERN.findall(clean_query):
        month_value = f"{year}-{month}"
        signals.months.add(month_value)
        signals.month_numbers.add(month)

    for month_name, year in _MONTH_NAME_PATTERN.findall(clean_query):
        month_number = _MONTH_NAME_MAP.get(month_name.lower())
        if not month_number:
            continue
        signals.month_numbers.add(month_number)
        if year:
            signals.months.add(f"{year}-{month_number}")

    for value in _INVOICE_PATTERN.findall(clean_query):
        if isinstance(value, tuple):
            for part in value:
                if part:
                    signals.invoice_numbers.add(part.strip().lower())
        elif value:
            signals.invoice_numbers.add(str(value).strip().lower())

    for value in _CHALLAN_PATTERN.findall(clean_query):
        if isinstance(value, tuple):
            for part in value:
                if part:
                    signals.challan_serial_numbers.add(part.strip().lower())
        elif value:
            signals.challan_serial_numbers.add(str(value).strip().lower())

    for amount_value in _AMOUNT_PATTERN.findall(clean_query):
        normalized_amount = _normalize_amount(amount_value)
        if normalized_amount and normalized_amount not in {"2024", "2025", "2026", "2027", "2028", "2029"}:
            signals.amounts.add(normalized_amount)

    signals.vendor_name_terms = {
        token
        for token in signals.query_tokens
        if token.isalpha() and len(token) >= 3 and token not in _STOPWORDS
    }

    return signals



def retrieve_structured_candidates(
    query: str,
    chunks: list[Any],
    *,
    risk_type: str | None = None,
    max_candidates: int | None = None,
) -> list[CandidateResult]:
    signals = extract_query_signals(query, explicit_risk_type=risk_type)
    candidates: list[CandidateResult] = []

    for chunk in chunks:
        metadata = _as_dict(_get(chunk, "chunk_metadata"))
        field_values = _build_field_values(chunk, metadata)
        score, matches = _score_chunk(
            field_values=field_values,
            source_type=str(_get(chunk, "source_type") or "").lower(),
            signals=signals,
        )

        if score <= 0:
            continue

        candidate = build_candidate_result(
            chunk,
            retrieval_source="structured",
            raw_score=score,
            debug_signals={
                "structured": {
                    "matches": matches,
                }
            },
        )
        candidates.append(candidate)

    candidates.sort(key=lambda item: (-item.raw_score, str(item.chunk_id)))

    if max_candidates is not None:
        candidates = candidates[: max(1, max_candidates)]

    for rank, candidate in enumerate(candidates, start=1):
        candidate.rank = rank

    return candidates



def _score_chunk(
    *,
    field_values: dict[str, set[str]],
    source_type: str,
    signals: QuerySignals,
) -> tuple[float, dict[str, Any]]:
    score = 0.0
    matches: dict[str, Any] = {}

    risk_type_matches = _intersect(field_values.get("risk_type", set()), signals.risk_types)
    if risk_type_matches:
        score += 3.0
        matches["risk_type"] = sorted(risk_type_matches)

    section_matches = _intersect(field_values.get("tds_section", set()), signals.tds_sections)
    if section_matches:
        score += 1.8
        matches["tds_section"] = sorted(section_matches)

    month_values = field_values.get("deduction_month", set()) | field_values.get("transaction_month", set())
    exact_month_matches = _intersect(month_values, signals.months)
    if exact_month_matches:
        score += 1.6
        matches["month"] = sorted(exact_month_matches)
    else:
        month_number_matches = {
            month
            for month in month_values
            if any(month.endswith(f"-{month_num}") or month == month_num for month_num in signals.month_numbers)
        }
        if month_number_matches:
            score += 0.9
            matches["month_number"] = sorted(month_number_matches)

    for key, signal_values, field_keys, boost in (
        ("vendor_code", signals.vendor_codes, ["vendor_code"], 1.7),
        ("pan", signals.pan_values, ["vendor_pan", "supplier_pan", "pan"], 1.7),
        ("tan", signals.tan_values, ["tan"], 1.4),
        ("gstin", signals.gstin_values, ["gstin"], 1.7),
        ("invoice_number", signals.invoice_numbers, ["invoice_number"], 1.6),
        ("challan_serial", signals.challan_serial_numbers, ["challan_serial_no", "challan_serial"], 1.4),
        ("bsr_code", signals.bsr_codes, ["bsr_code"], 1.3),
    ):
        if not signal_values:
            continue

        chunk_values: set[str] = set()
        for field_name in field_keys:
            chunk_values.update(field_values.get(field_name, set()))

        identifier_matches = _intersect(chunk_values, signal_values)
        if identifier_matches:
            score += boost
            matches[key] = sorted(identifier_matches)

    if signals.amounts:
        amount_fields = (
            field_values.get("gross_amount", set())
            | field_values.get("shortfall", set())
            | field_values.get("tds_deducted", set())
            | field_values.get("tds_required", set())
            | field_values.get("tds_deposited", set())
            | field_values.get("tax_deposited", set())
            | field_values.get("amount_paid_or_credited", set())
        )
        amount_matches = _intersect(amount_fields, signals.amounts)
        if amount_matches:
            score += 1.5
            matches["amount"] = sorted(amount_matches)

    vendor_values = field_values.get("vendor_name", set()) | field_values.get("supplier_name", set())
    if signals.vendor_name_terms and vendor_values:
        vendor_blob = " ".join(sorted(vendor_values))
        matched_terms = [term for term in signals.vendor_name_terms if term in vendor_blob]
        if matched_terms:
            ratio = len(matched_terms) / max(1, len(signals.vendor_name_terms))
            score += 1.2 * ratio
            matches["vendor_name_terms"] = sorted(matched_terms)

    risk_intent = bool(signals.risk_types or ({"risk", "short", "mismatch", "missing", "duplicate", "flagged"} & signals.query_tokens))
    entity_intent = bool({"vendor", "invoice", "pan", "gstin", "tan", "code", "record", "details", "challan", "bsr"} & signals.query_tokens)

    if risk_intent and source_type == "risk_finding":
        score += 0.6
        matches["source_preference"] = "risk_finding"

    if entity_intent and source_type == "normalized_record":
        score += 0.4
        matches["source_preference"] = "normalized_record"

    return score, matches



def _build_field_values(chunk: Any, metadata: dict[str, Any]) -> dict[str, set[str]]:
    risk_data = _as_dict(metadata.get("risk_data"))
    values: dict[str, set[str]] = {}

    def _insert(name: str, value: Any) -> None:
        normalized = _normalize_values(value)
        if not normalized:
            return
        values.setdefault(name, set()).update(normalized)

    for field_name in (
        "risk_type",
        "severity",
        "record_category",
        "chunk_type",
        "vendor_name",
        "supplier_name",
        "vendor_code",
        "vendor_pan",
        "supplier_pan",
        "pan",
        "tan",
        "gstin",
        "invoice_number",
        "challan_serial_no",
        "challan_serial",
        "bsr_code",
        "tds_section",
        "deduction_month",
        "transaction_month",
        "gross_amount",
        "shortfall",
        "amount_paid_or_credited",
        "tds_deducted",
        "tds_required",
        "tds_deposited",
        "tax_deposited",
    ):
        _insert(field_name, metadata.get(field_name))
        if field_name not in metadata:
            _insert(field_name, risk_data.get(field_name))

    _insert("chunk_type", _get(chunk, "chunk_type"))
    _insert("source_type", _get(chunk, "source_type"))

    return values



def _normalize_values(value: Any) -> set[str]:
    if value is None:
        return set()

    if isinstance(value, dict):
        flattened: set[str] = set()
        for item in value.values():
            flattened.update(_normalize_values(item))
        return flattened

    if isinstance(value, list):
        flattened: set[str] = set()
        for item in value:
            flattened.update(_normalize_values(item))
        return flattened

    if isinstance(value, (int, float)):
        normalized_amount = _normalize_amount(value)
        return {normalized_amount} if normalized_amount else set()

    text = str(value).strip().lower()
    if not text:
        return set()

    normalized_amount = _normalize_amount(text)
    if normalized_amount and re.fullmatch(r"\d+(?:\.\d+)?", normalized_amount):
        return {text, normalized_amount}

    return {text}



def _normalize_amount(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip().replace(",", "")
    if not text:
        return None

    try:
        numeric = float(text)
    except ValueError:
        return None

    if numeric.is_integer():
        return str(int(numeric))
    return f"{numeric:.2f}".rstrip("0").rstrip(".")



def _intersect(left: set[str], right: set[str]) -> set[str]:
    if not left or not right:
        return set()
    return left & right



def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_PATTERN.findall(text or "")]



def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)



def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}
