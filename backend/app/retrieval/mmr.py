from __future__ import annotations

import math
import re

from app.retrieval.types import CandidateResult

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_./-]+")



def apply_mmr(
    candidates: list[CandidateResult],
    *,
    limit: int,
    lambda_param: float = 0.70,
    candidate_pool_size: int = 30,
    query_embedding: list[float] | None = None,
) -> list[CandidateResult]:
    if not candidates:
        return []

    safe_limit = max(1, limit)
    pool_size = max(safe_limit, candidate_pool_size)
    pool = list(candidates[:pool_size])
    if not pool:
        return []

    safe_lambda = min(max(lambda_param, 0.0), 1.0)

    selected_indices: list[int] = []
    remaining_indices = list(range(len(pool)))

    while remaining_indices and len(selected_indices) < safe_limit:
        best_index: int | None = None
        best_mmr = -math.inf
        best_relevance = -math.inf
        best_penalty = math.inf

        for index in remaining_indices:
            candidate = pool[index]
            relevance = _relevance(candidate, query_embedding)

            if not selected_indices:
                redundancy_penalty = 0.0
                mmr_score = relevance
            else:
                redundancy_penalty = max(
                    _candidate_similarity(candidate, pool[selected_index])
                    for selected_index in selected_indices
                )
                mmr_score = safe_lambda * relevance - (1.0 - safe_lambda) * redundancy_penalty

            if best_index is None:
                best_index = index
                best_mmr = mmr_score
                best_relevance = relevance
                best_penalty = redundancy_penalty
                continue

            if mmr_score > best_mmr + 1e-12:
                best_index = index
                best_mmr = mmr_score
                best_relevance = relevance
                best_penalty = redundancy_penalty
                continue

            if abs(mmr_score - best_mmr) <= 1e-12:
                if relevance > best_relevance + 1e-12:
                    best_index = index
                    best_mmr = mmr_score
                    best_relevance = relevance
                    best_penalty = redundancy_penalty
                    continue
                if abs(relevance - best_relevance) <= 1e-12 and str(candidate.chunk_id) < str(pool[best_index].chunk_id):
                    best_index = index
                    best_mmr = mmr_score
                    best_relevance = relevance
                    best_penalty = redundancy_penalty

        if best_index is None:
            break

        selected_candidate = pool[best_index]
        selected_candidate.debug_signals["mmr"] = {
            "selected": True,
            "lambda": safe_lambda,
            "relevance": best_relevance,
            "redundancy_penalty": best_penalty,
            "mmr_score": best_mmr,
        }

        selected_indices.append(best_index)
        remaining_indices.remove(best_index)

    selected = [pool[index] for index in selected_indices]
    for rank, candidate in enumerate(selected, start=1):
        candidate.rank = rank
        candidate.debug_signals["mmr_selected"] = True

    return selected



def _relevance(candidate: CandidateResult, query_embedding: list[float] | None) -> float:
    score = candidate.final_score or candidate.fused_score or candidate.raw_score
    if score > 0:
        return float(score)

    if query_embedding and candidate.embedding:
        return _cosine_similarity(query_embedding, candidate.embedding)

    return 0.0



def _candidate_similarity(left: CandidateResult, right: CandidateResult) -> float:
    if left.embedding and right.embedding:
        return _cosine_similarity(left.embedding, right.embedding)

    return _text_similarity(left.chunk_text, right.chunk_text)



def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0

    size = min(len(left), len(right))
    if size <= 0:
        return 0.0

    left_vector = left[:size]
    right_vector = right[:size]

    left_norm = math.sqrt(sum(value * value for value in left_vector))
    right_norm = math.sqrt(sum(value * value for value in right_vector))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    dot_product = sum(l * r for l, r in zip(left_vector, right_vector))
    return float(dot_product / (left_norm * right_norm))



def _text_similarity(left_text: str, right_text: str) -> float:
    left_tokens = set(_tokenize(left_text))
    right_tokens = set(_tokenize(right_text))

    if not left_tokens or not right_tokens:
        return 0.0

    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)

    if union == 0:
        return 0.0

    return intersection / union



def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_PATTERN.findall(text or "")]
