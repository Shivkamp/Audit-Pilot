from __future__ import annotations

from app.retrieval.structured import extract_query_signals
from app.retrieval.types import CandidateResult



def apply_deterministic_boosts(
    query: str,
    candidates: list[CandidateResult],
    *,
    explicit_risk_type: str | None = None,
) -> list[CandidateResult]:
    if not candidates:
        return []

    signals = extract_query_signals(query, explicit_risk_type=explicit_risk_type)
    risk_intent = bool(signals.risk_types or ({"risk", "flagged", "mismatch", "short", "missing", "duplicate"} & signals.query_tokens))
    entity_intent = bool({"vendor", "invoice", "pan", "gstin", "tan", "code", "record", "details", "challan", "bsr"} & signals.query_tokens)

    reranked: list[CandidateResult] = []
    for candidate in candidates:
        metadata = candidate.chunk_metadata or {}
        risk_data = metadata.get("risk_data") if isinstance(metadata.get("risk_data"), dict) else {}

        values = _collect_values(candidate, metadata, risk_data)

        boosts: dict[str, float] = {}

        if values["risk_type"] & signals.risk_types:
            boosts["risk_type_exact"] = 0.35

        if values["vendor_code"] & signals.vendor_codes:
            boosts["vendor_code_exact"] = 0.25

        if values["invoice_number"] & signals.invoice_numbers:
            boosts["invoice_number_exact"] = 0.25

        if values["pan"] & signals.pan_values:
            boosts["pan_exact"] = 0.25

        if values["tan"] & signals.tan_values:
            boosts["tan_exact"] = 0.2

        if values["gstin"] & signals.gstin_values:
            boosts["gstin_exact"] = 0.25

        if values["tds_section"] & signals.tds_sections:
            boosts["tds_section_exact"] = 0.2

        if values["month"] & signals.months:
            boosts["month_exact"] = 0.2
        elif any(month.endswith(f"-{month_num}") or month == month_num for month in values["month"] for month_num in signals.month_numbers):
            boosts["month_partial"] = 0.1

        if values["amount"] & signals.amounts:
            boosts["amount_exact"] = 0.2

        vendor_blob = " ".join(sorted(values["vendor_name"]))
        matched_vendor_terms = [term for term in signals.vendor_name_terms if term in vendor_blob]
        if matched_vendor_terms:
            ratio = len(matched_vendor_terms) / max(1, len(signals.vendor_name_terms))
            boosts["vendor_name_partial"] = round(0.2 * ratio, 4)

        if risk_intent and candidate.source_type == "risk_finding":
            boosts["risk_finding_preference"] = 0.15

        if entity_intent and candidate.source_type == "normalized_record":
            boosts["normalized_record_preference"] = 0.12

        base_score = candidate.final_score or candidate.fused_score or candidate.raw_score
        total_boost = sum(boosts.values())
        candidate.final_score = base_score + total_boost

        candidate.debug_signals["deterministic_boosts"] = boosts
        candidate.debug_signals["deterministic_boost_total"] = total_boost

        reranked.append(candidate)

    reranked.sort(key=lambda item: (-item.final_score, -item.fused_score, str(item.chunk_id)))
    for rank, candidate in enumerate(reranked, start=1):
        candidate.rank = rank

    return reranked



def _collect_values(candidate: CandidateResult, metadata: dict, risk_data: dict) -> dict[str, set[str]]:
    values = {
        "risk_type": _merged_values(metadata.get("risk_type"), risk_data.get("risk_type"), candidate.chunk_type),
        "vendor_code": _merged_values(metadata.get("vendor_code"), risk_data.get("vendor_code")),
        "invoice_number": _merged_values(metadata.get("invoice_number"), risk_data.get("invoice_number")),
        "pan": _merged_values(metadata.get("vendor_pan"), metadata.get("supplier_pan"), metadata.get("pan"), risk_data.get("vendor_pan"), risk_data.get("pan")),
        "tan": _merged_values(metadata.get("tan"), risk_data.get("tan")),
        "gstin": _merged_values(metadata.get("gstin"), risk_data.get("gstin")),
        "tds_section": _merged_values(metadata.get("tds_section"), risk_data.get("tds_section")),
        "month": _merged_values(metadata.get("deduction_month"), metadata.get("transaction_month"), risk_data.get("deduction_month"), risk_data.get("transaction_month")),
        "amount": _merged_amount_values(
            metadata.get("gross_amount"),
            metadata.get("shortfall"),
            metadata.get("amount_paid_or_credited"),
            metadata.get("tds_required"),
            metadata.get("tds_deducted"),
            metadata.get("tds_deposited"),
            risk_data.get("gross_amount"),
            risk_data.get("shortfall"),
            risk_data.get("tds_required"),
            risk_data.get("tds_deducted"),
            risk_data.get("tds_deposited"),
        ),
        "vendor_name": _merged_values(metadata.get("vendor_name"), metadata.get("supplier_name"), risk_data.get("vendor_name"), risk_data.get("supplier_name")),
    }
    return values



def _merged_values(*raw_values: object) -> set[str]:
    merged: set[str] = set()
    for value in raw_values:
        if value is None:
            continue
        if isinstance(value, list):
            for item in value:
                merged.update(_merged_values(item))
            continue
        text = str(value).strip().lower()
        if text:
            merged.add(text)
    return merged



def _merged_amount_values(*raw_values: object) -> set[str]:
    merged: set[str] = set()
    for value in raw_values:
        normalized = _normalize_amount(value)
        if normalized:
            merged.add(normalized)
    return merged



def _normalize_amount(value: object) -> str | None:
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
