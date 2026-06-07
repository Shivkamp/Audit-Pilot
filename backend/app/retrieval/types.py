from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict
from uuid import UUID

RetrievalSource = Literal["vector", "keyword", "structured", "fused", "reranked"]


class RetrievalOptions(TypedDict, total=False):
    include_retrieval_debug: bool
    risk_type: str


@dataclass
class CandidateResult:
    chunk_id: UUID
    workspace_id: UUID
    source_type: str
    source_id: str | None
    chunk_type: str
    chunk_text: str
    chunk_metadata: dict[str, Any]
    retrieval_source: RetrievalSource
    raw_score: float = 0.0
    fused_score: float = 0.0
    final_score: float = 0.0
    rank: int = 0
    embedding: list[float] | None = None
    debug_signals: dict[str, Any] = field(default_factory=dict)


def build_candidate_result(
    chunk: Any,
    *,
    retrieval_source: RetrievalSource,
    raw_score: float,
    debug_signals: dict[str, Any] | None = None,
    include_embedding: bool = True,
) -> CandidateResult:
    metadata = _as_dict(_get(chunk, "chunk_metadata"))
    raw_embedding = _get(chunk, "embedding") if include_embedding else None
    vector = to_float_vector(raw_embedding)

    candidate = CandidateResult(
        chunk_id=_get(chunk, "id"),
        workspace_id=_get(chunk, "workspace_id"),
        source_type=str(_get(chunk, "source_type") or ""),
        source_id=_as_optional_str(_get(chunk, "source_id")),
        chunk_type=str(_get(chunk, "chunk_type") or ""),
        chunk_text=str(_get(chunk, "chunk_text") or ""),
        chunk_metadata=metadata,
        retrieval_source=retrieval_source,
        raw_score=float(raw_score),
        fused_score=float(raw_score),
        final_score=float(raw_score),
        embedding=vector,
        debug_signals=dict(debug_signals or {}),
    )

    return candidate


def to_float_vector(value: object) -> list[float] | None:
    if not isinstance(value, list):
        return None

    vector: list[float] = []
    for item in value:
        try:
            vector.append(float(item))
        except (TypeError, ValueError):
            continue

    if not vector:
        return None

    return vector


def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text
