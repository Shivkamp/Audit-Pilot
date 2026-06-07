from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import STATUS_ARCHIVED
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceRepository:
    @staticmethod
    def create(db: Session, client_id: UUID, payload: WorkspaceCreate) -> Workspace:
        workspace = Workspace(client_id=client_id, **payload.model_dump())
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def get_by_id(db: Session, workspace_id: UUID) -> Workspace | None:
        return db.scalar(select(Workspace).where(Workspace.id == workspace_id))

    @staticmethod
    def get_by_client_id(db: Session, client_id: UUID) -> list[Workspace]:
        return list(
            db.scalars(
                select(Workspace)
                .where(Workspace.client_id == client_id)
                .order_by(Workspace.created_at.desc())
            )
        )

    @staticmethod
    def update(db: Session, workspace: Workspace, payload: WorkspaceUpdate) -> Workspace:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)

        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def archive(db: Session, workspace: Workspace) -> Workspace:
        workspace.status = STATUS_ARCHIVED
        db.commit()
        db.refresh(workspace)
        return workspace
