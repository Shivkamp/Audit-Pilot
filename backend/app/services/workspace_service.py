from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.workspace import Workspace
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace_access_service import WorkspaceAccessService


class WorkspaceService:
    @staticmethod
    def create_workspace(
        db: Session,
        client_id: UUID,
        payload: WorkspaceCreate,
        *,
        owner_user_id: UUID | None = None,
    ) -> Workspace:
        WorkspaceService._ensure_client_exists(db, client_id)
        workspace = WorkspaceRepository.create(db, client_id, payload)

        if owner_user_id is not None:
            WorkspaceAccessService.create_owner_membership(db, workspace.id, owner_user_id)

        return workspace

    @staticmethod
    def list_client_workspaces(
        db: Session,
        client_id: UUID,
        *,
        user_id: UUID | None = None,
        is_superuser: bool = False,
    ) -> list[Workspace]:
        WorkspaceService._ensure_client_exists(db, client_id)
        workspaces = WorkspaceRepository.get_by_client_id(db, client_id)

        if user_id is None or is_superuser:
            return workspaces

        workspace_ids_for_user = set(WorkspaceMemberRepository.list_workspace_ids_by_user(db, user_id))
        return [workspace for workspace in workspaces if workspace.id in workspace_ids_for_user]

    @staticmethod
    def get_workspace(db: Session, workspace_id: UUID) -> Workspace:
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if workspace is None:
            raise AppException(
                message="Workspace not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="WORKSPACE_NOT_FOUND",
            )
        return workspace

    @staticmethod
    def update_workspace(db: Session, workspace_id: UUID, payload: WorkspaceUpdate) -> Workspace:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        return WorkspaceRepository.update(db, workspace, payload)

    @staticmethod
    def archive_workspace(db: Session, workspace_id: UUID) -> Workspace:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        return WorkspaceRepository.archive(db, workspace)

    @staticmethod
    def _ensure_client_exists(db: Session, client_id: UUID) -> None:
        client = ClientRepository.get_by_id(db, client_id)
        if client is None:
            raise AppException(
                message="Client not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="CLIENT_NOT_FOUND",
            )
