from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.workspace_member import WorkspaceMember


class WorkspaceMemberRepository:
    @staticmethod
    def create(
        db: Session,
        *,
        workspace_id: UUID,
        user_id: UUID,
        role: str,
    ) -> WorkspaceMember:
        membership = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def get_by_id(db: Session, member_id: UUID) -> WorkspaceMember | None:
        return db.scalar(
            select(WorkspaceMember)
            .options(joinedload(WorkspaceMember.user))
            .where(WorkspaceMember.id == member_id)
        )

    @staticmethod
    def get_by_workspace_user(
        db: Session,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> WorkspaceMember | None:
        return db.scalar(
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )

    @staticmethod
    def list_by_workspace_id(db: Session, workspace_id: UUID) -> list[WorkspaceMember]:
        statement = (
            select(WorkspaceMember)
            .options(joinedload(WorkspaceMember.user))
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.created_at.asc(), WorkspaceMember.id.asc())
        )
        return list(db.scalars(statement))

    @staticmethod
    def list_workspace_ids_by_user(db: Session, user_id: UUID) -> list[UUID]:
        return list(
            db.scalars(
                select(WorkspaceMember.workspace_id).where(WorkspaceMember.user_id == user_id)
            )
        )

    @staticmethod
    def count_by_workspace_role(db: Session, workspace_id: UUID, role: str) -> int:
        statement = select(func.count(WorkspaceMember.id)).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.role == role,
        )
        return int(db.scalar(statement) or 0)

    @staticmethod
    def update_role(db: Session, membership: WorkspaceMember, role: str) -> WorkspaceMember:
        membership.role = role
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def delete(db: Session, membership: WorkspaceMember) -> None:
        db.delete(membership)
        db.commit()
