from __future__ import annotations

from typing import Any



def build_citation(
    *,
    source_type: str,
    source_id: str | None,
    chunk_id: str | None,
    document_id: str | None,
    chunk_type: str | None,
) -> dict[str, Any]:
    return _drop_none(
        {
            "source_type": source_type,
            "source_id": source_id,
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_type": chunk_type,
        }
    )



def build_normalized_record_source_trace(
    *,
    source_id: str,
    normalized_record: Any | None,
    extracted_record: Any | None,
) -> dict[str, Any]:
    if normalized_record is None:
        return {
            "source_type": "normalized_record",
            "source_id": source_id,
        }

    normalized_record_id = _to_str(_get(normalized_record, "id"))
    source_record_id = _to_str(_get(normalized_record, "source_record_id"))

    source_locations = []
    if extracted_record is not None:
        source_locations.append(_extract_location(extracted_record))

    return _drop_none(
        {
            "source_type": "normalized_record",
            "source_id": source_id,
            "normalized_record_id": normalized_record_id,
            "normalized_record_ids": [normalized_record_id] if normalized_record_id else [],
            "source_record_ids": [source_record_id] if source_record_id else [],
            "document_ids": _collect_document_ids(normalized_record, extracted_record),
            "source_locations": [loc for loc in source_locations if loc],
        }
    )



def build_risk_finding_source_trace(
    *,
    source_id: str,
    risk_finding: Any | None,
    normalized_records: list[Any],
    extracted_records_by_id: dict[str, Any],
) -> dict[str, Any]:
    if risk_finding is None:
        return {
            "source_type": "risk_finding",
            "source_id": source_id,
        }

    normalized_record_ids = [
        _to_str(_get(record, "id"))
        for record in normalized_records
        if _to_str(_get(record, "id"))
    ]
    source_record_ids = [
        _to_str(_get(record, "source_record_id"))
        for record in normalized_records
        if _to_str(_get(record, "source_record_id"))
    ]

    source_locations = []
    for record_id in source_record_ids:
        extracted_record = extracted_records_by_id.get(record_id)
        if extracted_record is None:
            continue
        location = _extract_location(extracted_record)
        if location:
            source_locations.append(location)

    return _drop_none(
        {
            "source_type": "risk_finding",
            "source_id": source_id,
            "risk_finding_id": _to_str(_get(risk_finding, "id")),
            "normalized_record_ids": _unique(normalized_record_ids),
            "source_record_ids": _unique(source_record_ids),
            "document_ids": _collect_document_ids(risk_finding, *normalized_records),
            "source_locations": source_locations,
        }
    )



def _extract_location(record: Any) -> dict[str, Any]:
    return _drop_none(
        {
            "document_id": _to_str(_get(record, "document_id")),
            "sheet_name": _get(record, "sheet_name"),
            "row_number": _get(record, "row_number"),
            "page_number": _get(record, "page_number"),
        }
    )



def _collect_document_ids(*records: Any) -> list[str]:
    document_ids: list[str] = []
    for record in records:
        if record is None:
            continue
        document_id = _to_str(_get(record, "document_id"))
        if document_id is None:
            continue
        document_ids.append(document_id)
    return _unique(document_ids)



def _unique(values: list[str]) -> list[str]:
    return [value for value in dict.fromkeys(values) if value]



def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)



def _to_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text



def _drop_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}
