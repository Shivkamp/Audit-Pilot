from __future__ import annotations

import math
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    KNOWLEDGE_QUERY_REQUIRED,
    RERANKER_PROVIDER_NONE,
    RETRIEVAL_FUSION_METHOD_RRF,
    RETRIEVAL_SOURCE_KEYWORD,
    RETRIEVAL_SOURCE_STRUCTURED,
    RETRIEVAL_SOURCE_VECTOR,
)
from app.core.exceptions import AppException
from app.embeddings.service import EmbeddingService
from app.repositories.knowledge_chunk_repository import KnowledgeChunkRepository
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.keyword import retrieve_keyword_candidates
from app.retrieval.mmr import apply_mmr
from app.retrieval.rerankers import NoopReranker
from app.retrieval.scoring import apply_deterministic_boosts
from app.retrieval.structured import retrieve_structured_candidates
from app.retrieval.types import CandidateResult, RetrievalOptions, build_candidate_result, to_float_vector
from app.services.workspace_service import WorkspaceService


class RetrievalService:
    @staticmethod
    def search_workspace(
        db: Session,
        workspace_id: UUID,
        query: str,
        limit: int,
        retrieval_options: RetrievalOptions | None = None,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        clean_query = (query or "").strip()
        if not clean_query:
            raise AppException(
                message="Query cannot be blank.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=KNOWLEDGE_QUERY_REQUIRED,
            )

        options = retrieval_options or {}
        include_debug = bool(options.get("include_retrieval_debug", False))
        explicit_risk_type = RetrievalService._as_optional_text(options.get("risk_type"))

        safe_limit = max(1, min(limit, settings.knowledge_search_max_limit))
        safe_final_limit = max(1, int(settings.final_evidence_limit))
        result_limit = min(safe_limit, safe_final_limit)
        candidate_pool_size = max(
            result_limit,
            int(settings.mmr_candidate_pool_size),
            int(settings.llm_rerank_top_n),
            30,
        )

        searchable_chunks = KnowledgeChunkRepository.get_searchable_chunks_by_workspace(
            db,
            workspace.id,
        )
        embedded_chunks = KnowledgeChunkRepository.get_embedded_chunks_by_workspace(
            db,
            workspace.id,
        )

        query_embedding: list[float] | None = None
        vector_candidates: list[CandidateResult] = []
        keyword_candidates: list[CandidateResult] = []
        structured_candidates: list[CandidateResult] = []

        if settings.retrieval_enable_vector:
            embedding_service = EmbeddingService()
            query_embedding = to_float_vector(embedding_service.embed_text(clean_query))
            vector_candidates = RetrievalService._vector_retrieve(
                query_embedding=query_embedding,
                chunks=embedded_chunks,
                max_candidates=candidate_pool_size,
            )

        if settings.retrieval_enable_keyword:
            keyword_candidates = retrieve_keyword_candidates(
                clean_query,
                searchable_chunks,
                max_candidates=candidate_pool_size,
            )

        if settings.retrieval_enable_structured:
            structured_candidates = retrieve_structured_candidates(
                clean_query,
                searchable_chunks,
                risk_type=explicit_risk_type,
                max_candidates=candidate_pool_size,
            )

        ranked_lists: dict[str, list[CandidateResult]] = {}
        if vector_candidates:
            ranked_lists[RETRIEVAL_SOURCE_VECTOR] = vector_candidates
        if keyword_candidates:
            ranked_lists[RETRIEVAL_SOURCE_KEYWORD] = keyword_candidates
        if structured_candidates:
            ranked_lists[RETRIEVAL_SOURCE_STRUCTURED] = structured_candidates

        if not ranked_lists:
            return {
                "workspace_id": workspace.id,
                "query": clean_query,
                "limit": result_limit,
                "results": [],
            }

        fusion_method = (settings.retrieval_fusion_method or "").strip().lower()
        if fusion_method == RETRIEVAL_FUSION_METHOD_RRF:
            fused_candidates = reciprocal_rank_fusion(
                ranked_lists,
                rrf_k=settings.rrf_k,
            )
        else:
            first_source = next(iter(ranked_lists))
            fused_candidates = list(ranked_lists[first_source])
            for candidate in fused_candidates:
                candidate.fused_score = candidate.raw_score
                candidate.final_score = candidate.raw_score
                candidate.debug_signals.setdefault("retrieval_sources", [first_source])

        reranked_candidates = fused_candidates
        if settings.deterministic_rerank_enabled:
            reranked_candidates = apply_deterministic_boosts(
                clean_query,
                reranked_candidates,
                explicit_risk_type=explicit_risk_type,
            )
        else:
            reranked_candidates.sort(
                key=lambda item: (-item.fused_score, str(item.chunk_id))
            )
            for rank, candidate in enumerate(reranked_candidates, start=1):
                candidate.rank = rank
                candidate.final_score = candidate.fused_score

        if settings.llm_rerank_enabled and (settings.reranker_provider or "").lower() != RERANKER_PROVIDER_NONE:
            reranker = RetrievalService._build_reranker()
            reranked_candidates = reranker.rerank(
                clean_query,
                reranked_candidates,
                int(settings.llm_rerank_top_n),
            )

        if settings.mmr_enabled:
            final_candidates = apply_mmr(
                reranked_candidates,
                limit=result_limit,
                lambda_param=float(settings.mmr_lambda),
                candidate_pool_size=int(settings.mmr_candidate_pool_size),
                query_embedding=query_embedding,
            )
        else:
            final_candidates = reranked_candidates[:result_limit]
            for rank, candidate in enumerate(final_candidates, start=1):
                candidate.rank = rank
                candidate.debug_signals["mmr_selected"] = False

        results = [
            RetrievalService._to_result_dict(item, include_debug=include_debug)
            for item in final_candidates
        ]

        return {
            "workspace_id": workspace.id,
            "query": clean_query,
            "limit": result_limit,
            "results": results,
        }

    @staticmethod
    def _vector_retrieve(
        *,
        query_embedding: list[float] | None,
        chunks: list[object],
        max_candidates: int,
    ) -> list[CandidateResult]:
        if not query_embedding:
            return []

        candidates: list[CandidateResult] = []
        for chunk in chunks:
            chunk_embedding = to_float_vector(getattr(chunk, "embedding", None))
            score = RetrievalService._cosine_similarity(query_embedding, chunk_embedding or [])
            if score <= 0:
                continue

            candidate = build_candidate_result(
                chunk,
                retrieval_source="vector",
                raw_score=score,
                debug_signals={
                    "vector": {
                        "cosine_similarity": score,
                    }
                },
            )
            candidates.append(candidate)

        candidates.sort(key=lambda item: (-item.raw_score, str(item.chunk_id)))
        candidates = candidates[: max(1, max_candidates)]

        for rank, candidate in enumerate(candidates, start=1):
            candidate.rank = rank

        return candidates

    @staticmethod
    def _to_result_dict(
        candidate: CandidateResult,
        *,
        include_debug: bool,
    ) -> dict:
        score = candidate.final_score or candidate.fused_score or candidate.raw_score
        payload = {
            "chunk_id": candidate.chunk_id,
            "score": score,
            "source_type": candidate.source_type,
            "source_id": candidate.source_id,
            "chunk_type": candidate.chunk_type,
            "chunk_text": candidate.chunk_text,
            "chunk_metadata": candidate.chunk_metadata,
        }

        if include_debug:
            payload["retrieval_debug"] = RetrievalService._serialize_debug_signals(candidate)

        return payload

    @staticmethod
    def _serialize_debug_signals(candidate: CandidateResult) -> dict:
        rrf_data = candidate.debug_signals.get("rrf", {})
        deterministic_boosts = candidate.debug_signals.get("deterministic_boosts", {})
        return {
            "retrieval_sources": candidate.debug_signals.get("retrieval_sources", []),
            "rrf_score": candidate.fused_score,
            "vector_score": RetrievalService._get_rrf_raw_score(rrf_data, RETRIEVAL_SOURCE_VECTOR),
            "keyword_score": RetrievalService._get_rrf_raw_score(rrf_data, RETRIEVAL_SOURCE_KEYWORD),
            "structured_score": RetrievalService._get_rrf_raw_score(rrf_data, RETRIEVAL_SOURCE_STRUCTURED),
            "mmr_selected": bool(candidate.debug_signals.get("mmr_selected", False)),
            "deterministic_boosts": deterministic_boosts,
            "deterministic_boost_total": candidate.debug_signals.get("deterministic_boost_total", 0.0),
        }

    @staticmethod
    def _get_rrf_raw_score(rrf_data: dict, source_name: str) -> float | None:
        source_payload = rrf_data.get(source_name)
        if isinstance(source_payload, dict):
            raw_score = source_payload.get("raw_score")
            if isinstance(raw_score, (int, float)):
                return float(raw_score)
        return None

    @staticmethod
    def _as_optional_text(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        return text.lower()

    @staticmethod
    def _build_reranker() -> NoopReranker:
        return NoopReranker()

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0

        size = min(len(left), len(right))
        if size <= 0:
            return 0.0

        left_vec = left[:size]
        right_vec = right[:size]

        left_norm = math.sqrt(sum(value * value for value in left_vec))
        right_norm = math.sqrt(sum(value * value for value in right_vec))

        if left_norm == 0 or right_norm == 0:
            return 0.0

        dot_product = sum(left_value * right_value for left_value, right_value in zip(left_vec, right_vec))
        return float(dot_product / (left_norm * right_norm))

    @staticmethod
    def _as_float_vector(value: object) -> list[float]:
        if not isinstance(value, list):
            return []

        vector: list[float] = []
        for item in value:
            try:
                vector.append(float(item))
            except (TypeError, ValueError):
                continue

        return vector
