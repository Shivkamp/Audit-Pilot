from __future__ import annotations

from typing import Any


def collect_available_citations(state: dict[str, Any]) -> list[dict[str, Any]]:
    available: list[dict[str, Any]] = []

    for evidence_item in state.get("evidence") or []:
        if not isinstance(evidence_item, dict):
            continue

        citation = evidence_item.get("citation")
        if isinstance(citation, dict):
            available.append(_normalize_citation(citation))

        source_type = evidence_item.get("source_type")
        source_id = evidence_item.get("source_id")
        if source_type and source_id:
            available.append(
                _normalize_citation(
                    {
                        "source_type": source_type,
                        "source_id": source_id,
                    }
                )
            )

    for trace in state.get("source_traces") or []:
        if not isinstance(trace, dict):
            continue

        source_type = trace.get("source_type")
        source_id = trace.get("source_id") or trace.get("risk_finding_id")
        if source_type and source_id:
            available.append(
                _normalize_citation(
                    {
                        "source_type": source_type,
                        "source_id": source_id,
                    }
                )
            )

    for finding in state.get("risk_findings") or []:
        if not isinstance(finding, dict):
            continue
        finding_id = finding.get("id")
        if not finding_id:
            continue
        available.append(
            _normalize_citation(
                {
                    "source_type": "risk_finding",
                    "source_id": finding_id,
                }
            )
        )

    return _dedupe_citations(available)


def keep_only_valid_citations(
    citations: list[dict[str, Any]],
    available: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not citations or not available:
        return []

    allowed_keys = {_citation_key(item) for item in available}
    filtered: list[dict[str, Any]] = []
    for citation in citations:
        key = _citation_key(citation)
        if key in allowed_keys:
            filtered.append(_normalize_citation(citation))

    return _dedupe_citations(filtered)


def attach_best_available_citations(
    current: list[dict[str, Any]],
    available: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    if current:
        return _dedupe_citations(current)[:limit]
    return _dedupe_citations(available)[:limit]


def _dedupe_citations(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for citation in citations:
        normalized = _normalize_citation(citation)
        key = _citation_key(normalized)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(normalized)

    return deduped


def _citation_key(citation: dict[str, Any]) -> tuple[str, str, str]:
    source_type = str(citation.get("source_type") or "")
    source_id = str(citation.get("source_id") or "")
    chunk_id = str(citation.get("chunk_id") or "")
    return source_type, source_id, chunk_id


def _normalize_citation(citation: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "source_type": citation.get("source_type"),
        "source_id": citation.get("source_id"),
        "chunk_id": citation.get("chunk_id"),
        "document_id": citation.get("document_id"),
        "chunk_type": citation.get("chunk_type"),
    }
    return {key: value for key, value in payload.items() if value is not None}
