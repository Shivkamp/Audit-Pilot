from __future__ import annotations

from typing import Any

from app.core.constants import (
    EMBEDDING_STATUS_PENDING,
    KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
    KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
)
from app.knowledge.text_formatters import (
    format_normalized_record_text,
    format_risk_finding_text,
    pick_common_knowledge_fields,
)



def build_chunks_from_normalized_records(records: list[Any]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []

    for record in records:
        normalized_data = _as_dict(_get(record, "normalized_data"))
        record_id = _to_str(_get(record, "id"))
        record_category = _clean_text(_get(record, "record_category")) or "unknown"

        chunk_metadata: dict[str, Any] = {
            "normalized_record_id": record_id,
            "record_category": record_category,
            "document_id": _to_str(_get(record, "document_id")),
            "source_record_id": _to_str(_get(record, "source_record_id")),
            "source_type": KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
            **pick_common_knowledge_fields(normalized_data),
        }

        chunks.append(
            {
                "workspace_id": _get(record, "workspace_id"),
                "document_id": _get(record, "document_id"),
                "source_type": KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
                "source_id": record_id,
                "chunk_type": f"{record_category}_record",
                "chunk_text": format_normalized_record_text(record),
                "chunk_metadata": _drop_none(chunk_metadata),
                "embedding_status": EMBEDDING_STATUS_PENDING,
            }
        )

    return chunks



def build_chunks_from_risk_findings(findings: list[Any]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []

    for finding in findings:
        risk_type = _clean_text(_get(finding, "risk_type")) or "unknown"
        finding_id = _to_str(_get(finding, "id"))
        related_ids = [
            _to_str(value)
            for value in (_get(finding, "related_normalized_record_ids") or [])
            if _to_str(value)
        ]

        chunk_metadata: dict[str, Any] = {
            "risk_finding_id": finding_id,
            "risk_type": risk_type,
            "severity": _clean_text(_get(finding, "severity")),
            "status": _clean_text(_get(finding, "status")),
            "workspace_id": _to_str(_get(finding, "workspace_id")),
            "document_id": _to_str(_get(finding, "document_id")),
            "primary_normalized_record_id": _to_str(_get(finding, "primary_normalized_record_id")),
            "related_normalized_record_ids": related_ids,
            "risk_data": _as_dict(_get(finding, "risk_data")),
        }

        chunks.append(
            {
                "workspace_id": _get(finding, "workspace_id"),
                "document_id": _get(finding, "document_id"),
                "source_type": KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
                "source_id": finding_id,
                "chunk_type": f"risk_{risk_type}",
                "chunk_text": format_risk_finding_text(finding),
                "chunk_metadata": _drop_none(chunk_metadata),
                "embedding_status": EMBEDDING_STATUS_PENDING,
            }
        )

    return chunks



def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)



def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text



def _to_str(value: Any) -> str | None:
    clean = _clean_text(value)
    if clean is None:
        return None
    return clean



def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}



def _drop_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}
