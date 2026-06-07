from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.constants import EMBEDDING_STATUS_EMBEDDED
from app.models.knowledge_chunk import KnowledgeChunk


class KnowledgeChunkRepository:
    @staticmethod
    def create(db: Session, payload: dict) -> KnowledgeChunk:
        chunk = KnowledgeChunk(**payload)
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def bulk_create(db: Session, payloads: Sequence[dict]) -> list[KnowledgeChunk]:
        if not payloads:
            return []

        chunks = [KnowledgeChunk(**payload) for payload in payloads]
        db.add_all(chunks)
        db.commit()
        for chunk in chunks:
            db.refresh(chunk)
        return chunks

    @staticmethod
    def get_by_id(db: Session, chunk_id: UUID) -> KnowledgeChunk | None:
        return db.scalar(select(KnowledgeChunk).where(KnowledgeChunk.id == chunk_id))

    @staticmethod
    def list_by_workspace(
        db: Session,
        workspace_id: UUID,
        *,
        source_type: str | None = None,
        chunk_type: str | None = None,
        embedding_status: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[KnowledgeChunk]:
        statement = select(KnowledgeChunk).where(KnowledgeChunk.workspace_id == workspace_id)
        statement = KnowledgeChunkRepository._apply_filters(
            statement,
            source_type=source_type,
            chunk_type=chunk_type,
            embedding_status=embedding_status,
        )
        statement = statement.order_by(KnowledgeChunk.created_at.desc(), KnowledgeChunk.id.desc())

        if limit is not None:
            statement = statement.limit(max(1, limit))

        statement = statement.offset(max(0, offset))
        return list(db.scalars(statement))

    @staticmethod
    def delete_by_workspace_id(db: Session, workspace_id: UUID) -> int:
        result = db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.workspace_id == workspace_id))
        db.commit()
        return int(result.rowcount or 0)

    @staticmethod
    def delete_by_document_id(db: Session, document_id: UUID) -> int:
        result = db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id))
        db.commit()
        return int(result.rowcount or 0)

    @staticmethod
    def count_by_workspace(db: Session, workspace_id: UUID) -> int:
        statement = select(func.count(KnowledgeChunk.id)).where(KnowledgeChunk.workspace_id == workspace_id)
        return int(db.scalar(statement) or 0)

    @staticmethod
    def count_by_workspace_filtered(
        db: Session,
        workspace_id: UUID,
        *,
        source_type: str | None = None,
        chunk_type: str | None = None,
        embedding_status: str | None = None,
    ) -> int:
        statement = select(func.count(KnowledgeChunk.id)).where(KnowledgeChunk.workspace_id == workspace_id)
        statement = KnowledgeChunkRepository._apply_filters(
            statement,
            source_type=source_type,
            chunk_type=chunk_type,
            embedding_status=embedding_status,
        )
        return int(db.scalar(statement) or 0)

    @staticmethod
    def get_summary_by_workspace(db: Session, workspace_id: UUID) -> dict:
        total_chunks = KnowledgeChunkRepository.count_by_workspace(db, workspace_id)

        source_rows = db.execute(
            select(KnowledgeChunk.source_type, func.count(KnowledgeChunk.id))
            .where(KnowledgeChunk.workspace_id == workspace_id)
            .group_by(KnowledgeChunk.source_type)
        ).all()

        chunk_type_rows = db.execute(
            select(KnowledgeChunk.chunk_type, func.count(KnowledgeChunk.id))
            .where(KnowledgeChunk.workspace_id == workspace_id)
            .group_by(KnowledgeChunk.chunk_type)
        ).all()

        embedding_status_rows = db.execute(
            select(KnowledgeChunk.embedding_status, func.count(KnowledgeChunk.id))
            .where(KnowledgeChunk.workspace_id == workspace_id)
            .group_by(KnowledgeChunk.embedding_status)
        ).all()

        return {
            "workspace_id": workspace_id,
            "total_chunks": total_chunks,
            "by_source_type": {source_type: int(count) for source_type, count in source_rows},
            "by_chunk_type": {chunk_type: int(count) for chunk_type, count in chunk_type_rows},
            "by_embedding_status": {
                embedding_status: int(count)
                for embedding_status, count in embedding_status_rows
            },
        }

    @staticmethod
    def get_embedded_chunks_by_workspace(db: Session, workspace_id: UUID) -> list[KnowledgeChunk]:
        statement = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.workspace_id == workspace_id)
            .where(KnowledgeChunk.embedding_status == EMBEDDING_STATUS_EMBEDDED)
            .where(KnowledgeChunk.embedding.is_not(None))
            .order_by(KnowledgeChunk.created_at.desc(), KnowledgeChunk.id.desc())
        )
        return list(db.scalars(statement))

    @staticmethod
    def get_searchable_chunks_by_workspace(
        db: Session,
        workspace_id: UUID,
        *,
        source_types: Sequence[str] | None = None,
        limit: int | None = None,
    ) -> list[KnowledgeChunk]:
        statement = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.workspace_id == workspace_id)
            .where(KnowledgeChunk.chunk_text.is_not(None))
            .order_by(KnowledgeChunk.created_at.desc(), KnowledgeChunk.id.desc())
        )

        if source_types:
            statement = statement.where(KnowledgeChunk.source_type.in_(source_types))

        if limit is not None:
            statement = statement.limit(max(1, int(limit)))

        return list(db.scalars(statement))

    @staticmethod
    def get_chunks_by_workspace_and_source_type(
        db: Session,
        workspace_id: UUID,
        source_type: str,
        *,
        limit: int | None = None,
    ) -> list[KnowledgeChunk]:
        statement = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.workspace_id == workspace_id)
            .where(KnowledgeChunk.source_type == source_type)
            .order_by(KnowledgeChunk.created_at.desc(), KnowledgeChunk.id.desc())
        )

        if limit is not None:
            statement = statement.limit(max(1, int(limit)))

        return list(db.scalars(statement))

    @staticmethod
    def update_embedding(
        db: Session,
        chunk_id: UUID,
        *,
        embedding: list[float] | None,
        embedding_model: str | None,
        embedding_provider: str | None,
        embedding_status: str,
        embedding_error: str | None = None,
    ) -> KnowledgeChunk | None:
        chunk = KnowledgeChunkRepository.get_by_id(db, chunk_id)
        if chunk is None:
            return None

        chunk.embedding = embedding
        chunk.embedding_model = embedding_model
        chunk.embedding_provider = embedding_provider
        chunk.embedding_status = embedding_status
        chunk.embedding_error = embedding_error
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def bulk_update_embeddings(db: Session, updates: Sequence[dict]) -> int:
        if not updates:
            return 0

        chunk_ids = [update["chunk_id"] for update in updates if update.get("chunk_id") is not None]
        if not chunk_ids:
            return 0

        chunks = list(
            db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(chunk_ids)))
        )
        chunks_by_id = {chunk.id: chunk for chunk in chunks}

        updated_count = 0
        for update in updates:
            chunk_id = update.get("chunk_id")
            if chunk_id is None:
                continue

            chunk = chunks_by_id.get(chunk_id)
            if chunk is None:
                continue

            chunk.embedding = update.get("embedding")
            chunk.embedding_model = update.get("embedding_model")
            chunk.embedding_provider = update.get("embedding_provider")
            chunk.embedding_status = update.get("embedding_status", chunk.embedding_status)
            chunk.embedding_error = update.get("embedding_error")
            updated_count += 1

        if updated_count > 0:
            db.commit()

        return updated_count

    @staticmethod
    def _apply_filters(
        statement,
        *,
        source_type: str | None,
        chunk_type: str | None,
        embedding_status: str | None,
    ):
        if source_type:
            statement = statement.where(KnowledgeChunk.source_type == source_type)

        if chunk_type:
            statement = statement.where(KnowledgeChunk.chunk_type == chunk_type)

        if embedding_status:
            statement = statement.where(KnowledgeChunk.embedding_status == embedding_status)

        return statement
