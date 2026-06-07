from __future__ import annotations

import re
from typing import Any

from app.retrieval.types import CandidateResult, build_candidate_result

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_./-]+")

_PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
_TAN_PATTERN = re.compile(r"\b[A-Z]{4}[0-9]{5}[A-Z]\b", re.IGNORECASE)
_GSTIN_PATTERN = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]\b", re.IGNORECASE)
_VENDOR_CODE_PATTERN = re.compile(r"\bV[0-9]{3,}\b", re.IGNORECASE)
_TDS_SECTION_PATTERN = re.compile(r"\b19[4-9][A-Z]?\b", re.IGNORECASE)
_MONTH_PATTERN = re.compile(r"\b20[0-9]{2}-(?:0[1-9]|1[0-2])\b")
_INVOICE_PATTERN = re.compile(r"\b(?:invoice|inv)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\-/]{3,})\b", re.IGNORECASE)
_CHALLAN_PATTERN = re.compile(r"\b(?:challan|cin)\s*(?:serial|no|number|#)?\s*[:\-]?\s*([A-Z0-9\-/]{3,})\b", re.IGNORECASE)
_BSR_PATTERN = re.compile(r"\b[0-9]{7}\b")



def retrieve_keyword_candidates(
    query: str,
    chunks: list[Any],
    *,
    max_candidates: int | None = None,
) -> list[CandidateResult]:
    clean_query = (query or "").strip()
    if not clean_query:
        return []

    query_tokens = _tokenize(clean_query)
    if not query_tokens:
        return []

    query_text = clean_query.lower()
    query_identifiers = _extract_identifiers(clean_query)

    candidates: list[CandidateResult] = []
    for chunk in chunks:
        metadata = _as_dict(_get(chunk, "chunk_metadata"))
        chunk_text = str(_get(chunk, "chunk_text") or "")
        metadata_text = _metadata_to_text(metadata)
        searchable_text = f"{chunk_text} {metadata_text}".strip().lower()

        if not searchable_text:
            continue

        document_tokens = set(_tokenize(searchable_text))
        token_matches = [token for token in query_tokens if token in document_tokens]
        token_match_score = len(token_matches) / max(1, len(query_tokens))

        substring_hits = [
            token
            for token in query_tokens
            if len(token) >= 4 and token in searchable_text
        ]
        substring_score = min(0.6, len(substring_hits) * 0.1)

        phrase_boost = 1.5 if query_text in searchable_text else 0.0
        all_tokens_boost = 0.4 if token_matches and len(token_matches) == len(query_tokens) else 0.0

        identifier_hits = [
            value
            for value in query_identifiers
            if value in searchable_text
        ]
        identifier_score = len(identifier_hits) * 1.1

        score = token_match_score + substring_score + phrase_boost + all_tokens_boost + identifier_score
        if score <= 0:
            continue

        candidate = build_candidate_result(
            chunk,
            retrieval_source="keyword",
            raw_score=score,
            debug_signals={
                "keyword": {
                    "token_match_count": len(token_matches),
                    "substring_match_count": len(substring_hits),
                    "identifier_hit_count": len(identifier_hits),
                    "phrase_match": phrase_boost > 0,
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



def _extract_identifiers(text: str) -> set[str]:
    identifiers: set[str] = set()
    upper = (text or "").upper()

    for pattern in (
        _PAN_PATTERN,
        _TAN_PATTERN,
        _GSTIN_PATTERN,
        _VENDOR_CODE_PATTERN,
        _TDS_SECTION_PATTERN,
        _MONTH_PATTERN,
        _BSR_PATTERN,
    ):
        for match in pattern.findall(upper):
            if isinstance(match, tuple):
                identifiers.update(part.lower() for part in match if part)
            else:
                identifiers.add(str(match).lower())

    for pattern in (_INVOICE_PATTERN, _CHALLAN_PATTERN):
        for match in pattern.findall(text or ""):
            if isinstance(match, tuple):
                identifiers.update(part.lower() for part in match if part)
            else:
                identifiers.add(str(match).lower())

    return {value for value in identifiers if value}



def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_PATTERN.findall(text or "")]



def _metadata_to_text(payload: dict[str, Any]) -> str:
    pieces: list[str] = []

    def _walk(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for item in value.values():
                _walk(item)
            return
        if isinstance(value, list):
            for item in value:
                _walk(item)
            return

        text = str(value).strip()
        if text:
            pieces.append(text)

    _walk(payload)
    return " ".join(pieces)



def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)



def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}
