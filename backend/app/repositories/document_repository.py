from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import DOCUMENT_STATUS_DELETED
from app.models.document import Document
from app.schemas.document import DocumentCreate


class DocumentRepository:
    @staticmethod
    def create(db: Session, payload: DocumentCreate) -> Document:
        document = Document(**payload.model_dump())
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_by_id(db: Session, document_id: UUID) -> Document | None:
        return db.scalar(select(Document).where(Document.id == document_id))

    @staticmethod
    def get_document_by_id(db: Session, document_id: UUID) -> Document | None:
        return DocumentRepository.get_by_id(db, document_id)

    @staticmethod
    def list_by_workspace_id(
        db: Session,
        workspace_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> list[Document]:
        statement = select(Document).where(Document.workspace_id == workspace_id)
        if not include_deleted:
            statement = statement.where(Document.status != DOCUMENT_STATUS_DELETED)

        statement = statement.order_by(Document.created_at.desc())
        return list(db.scalars(statement))

    @staticmethod
    def update_status(db: Session, document: Document, status: str) -> Document:
        document.status = status
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def update_classification(
        db: Session,
        document: Document,
        *,
        document_type: str,
        classification_confidence: float | None,
        classification_method: str | None,
        classification_reason: dict | None,
        classified_at: datetime | None,
    ) -> Document:
        document.document_type = document_type
        document.classification_confidence = classification_confidence
        document.classification_method = classification_method
        document.classification_reason = classification_reason
        document.classified_at = classified_at
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_workspace_documents_with_classification(
        db: Session,
        workspace_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> list[Document]:
        statement = select(Document).where(Document.workspace_id == workspace_id)
        if not include_deleted:
            statement = statement.where(Document.status != DOCUMENT_STATUS_DELETED)

        statement = statement.order_by(Document.created_at.desc())
        return list(db.scalars(statement))
