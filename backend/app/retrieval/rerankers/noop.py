from __future__ import annotations

from app.retrieval.rerankers.base import RerankerProvider
from app.retrieval.types import CandidateResult


class NoopReranker(RerankerProvider):
    def rerank(
        self,
        query: str,
        candidates: list[CandidateResult],
        top_n: int,
    ) -> list[CandidateResult]:
        _ = query
        _ = top_n
        return list(candidates)
