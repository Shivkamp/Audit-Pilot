from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    EMBEDDING_STATUS_EMBEDDED,
    EMBEDDING_STATUS_FAILED,
    KNOWLEDGE_ALLOWED_EMBEDDING_STATUSES,
    KNOWLEDGE_ALLOWED_SOURCE_TYPES,
    KNOWLEDGE_INVALID_EMBEDDING_STATUS,
    KNOWLEDGE_UNSUPPORTED_SOURCE_TYPE,
)
from app.core.exceptions import AppException
from app.embeddings.service import EmbeddingService
from app.knowledge.chunk_builders import (
    build_chunks_from_normalized_records,
    build_chunks_from_risk_findings,
)
from app.repositories.knowledge_chunk_repository import KnowledgeChunkRepository
from app.repositories.normalization_repository import NormalizationRepository
from app.repositories.risk_finding_repository import RiskFindingRepository
from app.services.workspace_service import WorkspaceService


class KnowledgeIndexService:
    @staticmethod
    def rebuild_workspace_index(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        KnowledgeChunkRepository.delete_by_workspace_id(db, workspace.id)

        normalized_records = NormalizationRepository.get_by_workspace_id(db, workspace.id)
        risk_findings = RiskFindingRepository.get_by_workspace_id(db, workspace.id)

        normalized_chunks = build_chunks_from_normalized_records(normalized_records)
        risk_chunks = build_chunks_from_risk_findings(risk_findings)
        chunk_payloads = [*normalized_chunks, *risk_chunks]

        created_chunks = KnowledgeChunkRepository.bulk_create(db, chunk_payloads)
        embedded_chunks, failed_chunks = KnowledgeIndexService._embed_chunks(db, created_chunks)

        return {
            "workspace_id": workspace.id,
            "total_chunks": len(created_chunks),
            "normalized_record_chunks": len(normalized_chunks),
            "risk_finding_chunks": len(risk_chunks),
            "embedded_chunks": embedded_chunks,
            "failed_chunks": failed_chunks,
        }

    @staticmethod
    def get_workspace_index_summary(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        return KnowledgeChunkRepository.get_summary_by_workspace(db, workspace.id)

    @staticmethod
    def index_document(db: Session, document_id: UUID) -> dict:
        KnowledgeChunkRepository.delete_by_document_id(db, document_id)

        normalized_records = NormalizationRepository.get_all_by_document_id(db, document_id)
        risk_findings = RiskFindingRepository.get_by_document_id(db, document_id)

        normalized_chunks = build_chunks_from_normalized_records(normalized_records)
        risk_chunks = build_chunks_from_risk_findings(risk_findings)
        chunk_payloads = [*normalized_chunks, *risk_chunks]

        created_chunks = KnowledgeChunkRepository.bulk_create(db, chunk_payloads)

        embedded_chunks, failed_chunks = KnowledgeIndexService._embed_chunks(db, created_chunks)

        return {
            "document_id": document_id,
            "total_chunks": len(created_chunks),
            "normalized_record_chunks": len(normalized_chunks),
            "risk_finding_chunks": len(risk_chunks),
            "embedded_chunks": embedded_chunks,
            "failed_chunks": failed_chunks,
        }

    @staticmethod
    def _embed_chunks(db: Session, created_chunks: list) -> tuple[int, int]:
        if not created_chunks:
            return 0, 0

        embedding_service: EmbeddingService | None = None
        provider_error_message: str | None = None
        try:
            embedding_service = EmbeddingService()
        except AppException:
            provider_error_message = "Embedding provider initialization failed."

        embedded_chunks = 0
        failed_chunks = 0
        updates: list[dict] = []

        for chunk in created_chunks:
            if embedding_service is None:
                updates.append({
                    "chunk_id": chunk.id,
                    "embedding": None,
                    "embedding_model": None,
                    "embedding_provider": None,
                    "embedding_status": EMBEDDING_STATUS_FAILED,
                    "embedding_error": provider_error_message,
                })
                failed_chunks += 1
                continue

            try:
                vector = embedding_service.embed_text(chunk.chunk_text or "")
                updates.append({
                    "chunk_id": chunk.id,
                    "embedding": vector,
                    "embedding_model": embedding_service.model_name,
                    "embedding_provider": embedding_service.provider_name,
                    "embedding_status": EMBEDDING_STATUS_EMBEDDED,
                    "embedding_error": None,
                })
                embedded_chunks += 1
            except Exception:
                updates.append({
                    "chunk_id": chunk.id,
                    "embedding": None,
                    "embedding_model": embedding_service.model_name,
                    "embedding_provider": embedding_service.provider_name,
                    "embedding_status": EMBEDDING_STATUS_FAILED,
                    "embedding_error": "Embedding generation failed for this chunk.",
                })
                failed_chunks += 1

        KnowledgeChunkRepository.bulk_update_embeddings(db, updates)
        return embedded_chunks, failed_chunks

    @staticmethod
    def delete_workspace_index(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        deleted_count = KnowledgeChunkRepository.delete_by_workspace_id(db, workspace.id)

        return {
            "workspace_id": workspace.id,
            "deleted_chunks": deleted_count,
        }

    @staticmethod
    def list_workspace_chunks(
        db: Session,
        workspace_id: UUID,
        *,
        source_type: str | None,
        chunk_type: str | None,
        embedding_status: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        if source_type and source_type not in KNOWLEDGE_ALLOWED_SOURCE_TYPES:
            raise AppException(
                message="Unsupported knowledge source type filter.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=KNOWLEDGE_UNSUPPORTED_SOURCE_TYPE,
            )

        if embedding_status and embedding_status not in KNOWLEDGE_ALLOWED_EMBEDDING_STATUSES:
            raise AppException(
                message="Invalid embedding status filter.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=KNOWLEDGE_INVALID_EMBEDDING_STATUS,
            )

        safe_limit = max(1, min(limit, settings.knowledge_api_max_limit))
        safe_offset = max(0, offset)

        chunks = KnowledgeChunkRepository.list_by_workspace(
            db,
            workspace.id,
            source_type=source_type,
            chunk_type=chunk_type,
            embedding_status=embedding_status,
            limit=safe_limit,
            offset=safe_offset,
        )
        total_records = KnowledgeChunkRepository.count_by_workspace_filtered(
            db,
            workspace.id,
            source_type=source_type,
            chunk_type=chunk_type,
            embedding_status=embedding_status,
        )

        return {
            "workspace_id": workspace.id,
            "total_records": total_records,
            "limit": safe_limit,
            "offset": safe_offset,
            "chunks": chunks,
        }
