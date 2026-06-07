from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.constants import (
    AUTH_FORBIDDEN,
    WORKSPACE_ACCESS_DENIED,
    WORKSPACE_LAST_OWNER_REQUIRED,
    WORKSPACE_ROLE_ADMIN,
    WORKSPACE_ROLE_EDITOR,
    WORKSPACE_ROLE_OWNER,
    WORKSPACE_ROLE_REQUIRED,
    WORKSPACE_ROLE_VIEWER,
)
from app.core.exceptions import AppException
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.repositories.workspace_member_repository import WorkspaceMemberRepository


class WorkspaceAccessService:
    @staticmethod
    def get_membership(
        db: Session,
        workspace_id: UUID,
        user_id: UUID,
    ) -> WorkspaceMember | None:
        return WorkspaceMemberRepository.get_by_workspace_user(
            db,
            workspace_id=workspace_id,
            user_id=user_id,
        )

    @staticmethod
    def require_workspace_access(
        db: Session,
        workspace_id: UUID,
        user: User,
        allowed_roles: set[str] | None = None,
    ) -> WorkspaceMember | None:
        if user.is_superuser:
            return None

        membership = WorkspaceAccessService.get_membership(db, workspace_id, user.id)
        if membership is None:
            raise AppException(
                message="You do not have access to this workspace.",
                status_code=status.HTTP_403_FORBIDDEN,
                error_code=WORKSPACE_ACCESS_DENIED,
            )

        if allowed_roles is not None and membership.role not in allowed_roles:
            raise AppException(
                message="You do not have the required workspace role for this action.",
                status_code=status.HTTP_403_FORBIDDEN,
                error_code=WORKSPACE_ROLE_REQUIRED,
            )

        return membership

    @staticmethod
    def require_workspace_role(
        db: Session,
        workspace_id: UUID,
        user: User,
        allowed_roles: set[str],
    ) -> WorkspaceMember | None:
        return WorkspaceAccessService.require_workspace_access(
            db,
            workspace_id,
            user,
            allowed_roles=allowed_roles,
        )

    @staticmethod
    def can_manage_members(
        actor_role: str,
        target_role: str | None,
        new_role: str | None,
    ) -> bool:
        if actor_role == WORKSPACE_ROLE_OWNER:
            return True

        if actor_role == WORKSPACE_ROLE_ADMIN:
            if target_role not in {WORKSPACE_ROLE_EDITOR, WORKSPACE_ROLE_VIEWER, None}:
                return False
            if new_role not in {WORKSPACE_ROLE_EDITOR, WORKSPACE_ROLE_VIEWER, None}:
                return False
            return True

        return False

    @staticmethod
    def create_owner_membership(db: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember:
        existing_membership = WorkspaceMemberRepository.get_by_workspace_user(
            db,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        if existing_membership is None:
            return WorkspaceMemberRepository.create(
                db,
                workspace_id=workspace_id,
                user_id=user_id,
                role=WORKSPACE_ROLE_OWNER,
            )

        if existing_membership.role != WORKSPACE_ROLE_OWNER:
            return WorkspaceMemberRepository.update_role(db, existing_membership, WORKSPACE_ROLE_OWNER)

        return existing_membership

    @staticmethod
    def ensure_owner_not_last(
        db: Session,
        *,
        workspace_id: UUID,
        role: str,
    ) -> None:
        if role != WORKSPACE_ROLE_OWNER:
            return

        owner_count = WorkspaceMemberRepository.count_by_workspace_role(
            db,
            workspace_id,
            WORKSPACE_ROLE_OWNER,
        )
        if owner_count <= 1:
            raise AppException(
                message="Workspace must have at least one owner.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=WORKSPACE_LAST_OWNER_REQUIRED,
            )

    @staticmethod
    def ensure_member_management_allowed(
        actor_role: str,
        target_role: str | None,
        new_role: str | None,
    ) -> None:
        if WorkspaceAccessService.can_manage_members(actor_role, target_role, new_role):
            return

        raise AppException(
            message="You are not allowed to manage this workspace member.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=AUTH_FORBIDDEN,
        )
