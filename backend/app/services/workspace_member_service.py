from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.constants import (
    USER_NOT_FOUND,
    WORKSPACE_ADMIN_ROLES,
    WORKSPACE_MEMBER_ALREADY_EXISTS,
    WORKSPACE_MEMBER_NOT_FOUND,
    WORKSPACE_ROLE_OWNER,
)
from app.core.exceptions import AppException
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.services.workspace_access_service import WorkspaceAccessService


class WorkspaceMemberService:
    @staticmethod
    def list_workspace_members(
        db: Session,
        workspace_id: UUID,
        actor_user: User,
    ) -> list[WorkspaceMember]:
        WorkspaceAccessService.require_workspace_access(
            db,
            workspace_id,
            actor_user,
        )
        return WorkspaceMemberRepository.list_by_workspace_id(db, workspace_id)

    @staticmethod
    def add_workspace_member(
        db: Session,
        workspace_id: UUID,
        actor_user: User,
        *,
        email: str,
        role: str,
    ) -> WorkspaceMember:
        actor_membership = WorkspaceAccessService.require_workspace_role(
            db,
            workspace_id,
            actor_user,
            WORKSPACE_ADMIN_ROLES,
        )
        actor_role = actor_membership.role if actor_membership is not None else WORKSPACE_ROLE_OWNER

        target_user = UserRepository.get_by_email(db, email)
        if target_user is None:
            raise AppException(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=USER_NOT_FOUND,
            )

        existing_membership = WorkspaceMemberRepository.get_by_workspace_user(
            db,
            workspace_id=workspace_id,
            user_id=target_user.id,
        )
        if existing_membership is not None:
            raise AppException(
                message="User is already a workspace member.",
                status_code=status.HTTP_409_CONFLICT,
                error_code=WORKSPACE_MEMBER_ALREADY_EXISTS,
            )

        WorkspaceAccessService.ensure_member_management_allowed(
            actor_role=actor_role,
            target_role=None,
            new_role=role,
        )

        return WorkspaceMemberRepository.create(
            db,
            workspace_id=workspace_id,
            user_id=target_user.id,
            role=role,
        )

    @staticmethod
    def update_workspace_member_role(
        db: Session,
        workspace_id: UUID,
        member_id: UUID,
        actor_user: User,
        *,
        role: str,
    ) -> WorkspaceMember:
        actor_membership = WorkspaceAccessService.require_workspace_role(
            db,
            workspace_id,
            actor_user,
            WORKSPACE_ADMIN_ROLES,
        )
        actor_role = actor_membership.role if actor_membership is not None else WORKSPACE_ROLE_OWNER

        target_membership = WorkspaceMemberRepository.get_by_id(db, member_id)
        if target_membership is None or target_membership.workspace_id != workspace_id:
            raise AppException(
                message="Workspace member not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=WORKSPACE_MEMBER_NOT_FOUND,
            )

        WorkspaceAccessService.ensure_member_management_allowed(
            actor_role=actor_role,
            target_role=target_membership.role,
            new_role=role,
        )

        if target_membership.role == role:
            return target_membership

        if target_membership.role == WORKSPACE_ROLE_OWNER and role != WORKSPACE_ROLE_OWNER:
            WorkspaceAccessService.ensure_owner_not_last(
                db,
                workspace_id=workspace_id,
                role=target_membership.role,
            )

        return WorkspaceMemberRepository.update_role(db, target_membership, role)

    @staticmethod
    def remove_workspace_member(
        db: Session,
        workspace_id: UUID,
        member_id: UUID,
        actor_user: User,
    ) -> WorkspaceMember:
        actor_membership = WorkspaceAccessService.require_workspace_role(
            db,
            workspace_id,
            actor_user,
            WORKSPACE_ADMIN_ROLES,
        )
        actor_role = actor_membership.role if actor_membership is not None else WORKSPACE_ROLE_OWNER

        target_membership = WorkspaceMemberRepository.get_by_id(db, member_id)
        if target_membership is None or target_membership.workspace_id != workspace_id:
            raise AppException(
                message="Workspace member not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=WORKSPACE_MEMBER_NOT_FOUND,
            )

        WorkspaceAccessService.ensure_member_management_allowed(
            actor_role=actor_role,
            target_role=target_membership.role,
            new_role=None,
        )

        WorkspaceAccessService.ensure_owner_not_last(
            db,
            workspace_id=workspace_id,
            role=target_membership.role,
        )

        WorkspaceMemberRepository.delete(db, target_membership)
        return target_membership
