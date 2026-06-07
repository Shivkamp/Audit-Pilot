from __future__ import annotations

from abc import ABC, abstractmethod

from app.retrieval.types import CandidateResult


class RerankerProvider(ABC):
    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: list[CandidateResult],
        top_n: int,
    ) -> list[CandidateResult]:
        raise NotImplementedError
