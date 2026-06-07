from __future__ import annotations

from dataclasses import replace

from app.retrieval.types import CandidateResult


def reciprocal_rank_fusion(
    candidate_lists: dict[str, list[CandidateResult]],
    *,
    rrf_k: int = 60,
) -> list[CandidateResult]:
    """Fuse multiple ranked candidate lists using Reciprocal Rank Fusion."""
    safe_rrf_k = max(1, int(rrf_k))

    combined_candidates: dict[object, CandidateResult] = {}
    fused_scores: dict[object, float] = {}

    for source_name, candidates in candidate_lists.items():
        for rank, candidate in enumerate(candidates, start=1):
            chunk_key = candidate.chunk_id
            contribution = 1.0 / (safe_rrf_k + rank)

            fused_scores[chunk_key] = fused_scores.get(chunk_key, 0.0) + contribution

            if chunk_key not in combined_candidates:
                combined = replace(candidate)
                combined.retrieval_source = "fused"
                combined.debug_signals = dict(candidate.debug_signals or {})
                combined_candidates[chunk_key] = combined

            debug = combined_candidates[chunk_key].debug_signals.setdefault("rrf", {})
            debug[source_name] = {
                "rank": rank,
                "contribution": contribution,
                "raw_score": candidate.raw_score,
            }

    fused: list[CandidateResult] = []
    for chunk_key, candidate in combined_candidates.items():
        candidate.fused_score = fused_scores.get(chunk_key, 0.0)
        candidate.final_score = candidate.fused_score
        candidate.debug_signals["retrieval_sources"] = sorted(
            candidate.debug_signals.get("rrf", {}).keys()
        )
        fused.append(candidate)

    fused.sort(key=lambda item: (-item.fused_score, str(item.chunk_id)))
    for rank, candidate in enumerate(fused, start=1):
        candidate.rank = rank

    return fused


def rrf_fuse(
    candidate_lists: dict[str, list[CandidateResult]],
    *,
    rrf_k: int = 60,
) -> list[CandidateResult]:
    """Alias kept for call-site readability."""
    return reciprocal_rank_fusion(candidate_lists, rrf_k=rrf_k)
