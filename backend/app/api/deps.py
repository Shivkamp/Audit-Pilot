from __future__ import annotations

from collections.abc import Callable, Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.constants import (
    AUTH_INACTIVE_USER,
    AUTH_TOKEN_INVALID,
    DOCUMENT_STATUS_DELETED,
    RISK_FINDING_NOT_FOUND,
    RISK_RULE_CONFIG_NOT_FOUND,
)
from app.core.exceptions import AppException
from app.db.session import get_db as _get_db
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.models.risk_finding import RiskFinding
from app.models.risk_rule_config import RiskRuleConfig
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.repositories.document_repository import DocumentRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.risk_finding_repository import RiskFindingRepository
from app.repositories.risk_rule_config_repository import RiskRuleConfigRepository
from app.services.auth_service import AuthService
from app.services.workspace_access_service import WorkspaceAccessService

_bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    if credentials is None or not credentials.credentials:
        raise AppException(
            message="Authentication credentials were not provided.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=AUTH_TOKEN_INVALID,
        )

    return AuthService.get_current_user_from_token(db, credentials.credentials)


def require_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise AppException(
            message="User account is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=AUTH_INACTIVE_USER,
        )
    return current_user


CurrentUser = Annotated[User, Depends(require_active_user)]


def get_workspace_member(db: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
    return WorkspaceAccessService.get_membership(db, workspace_id, user_id)


def require_workspace_access(
    workspace_id: UUID,
    *,
    db: Session,
    current_user: User,
    allowed_roles: set[str] | None = None,
) -> WorkspaceMember | None:
    return WorkspaceAccessService.require_workspace_access(
        db,
        workspace_id,
        current_user,
        allowed_roles=allowed_roles,
    )


def require_workspace_role(
    workspace_id: UUID,
    *,
    db: Session,
    current_user: User,
    allowed_roles: set[str],
) -> WorkspaceMember | None:
    return WorkspaceAccessService.require_workspace_role(
        db,
        workspace_id,
        current_user,
        allowed_roles,
    )


def workspace_access_dependency(
    *,
    allowed_roles: set[str] | None = None,
) -> Callable[..., WorkspaceMember | None]:
    def _dependency(
        workspace_id: UUID,
        db: DbSession,
        current_user: CurrentUser,
    ) -> WorkspaceMember | None:
        return require_workspace_access(
            workspace_id,
            db=db,
            current_user=current_user,
            allowed_roles=allowed_roles,
        )

    return _dependency


def workspace_role_dependency(*, allowed_roles: set[str]) -> Callable[..., WorkspaceMember | None]:
    def _dependency(
        workspace_id: UUID,
        db: DbSession,
        current_user: CurrentUser,
    ) -> WorkspaceMember | None:
        return require_workspace_role(
            workspace_id,
            db=db,
            current_user=current_user,
            allowed_roles=allowed_roles,
        )

    return _dependency


def _get_document_for_access(
    db: Session,
    document_id: UUID,
    *,
    include_deleted: bool,
) -> Document:
    document = DocumentRepository.get_by_id(db, document_id)
    if document is None or (not include_deleted and document.status == DOCUMENT_STATUS_DELETED):
        raise AppException(
            message="Document not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="DOCUMENT_NOT_FOUND",
        )
    return document


def document_access_dependency(
    *,
    allowed_roles: set[str] | None = None,
    include_deleted: bool = False,
) -> Callable[..., Document]:
    def _dependency(
        document_id: UUID,
        db: DbSession,
        current_user: CurrentUser,
    ) -> Document:
        document = _get_document_for_access(
            db,
            document_id,
            include_deleted=include_deleted,
        )
        require_workspace_access(
            document.workspace_id,
            db=db,
            current_user=current_user,
            allowed_roles=allowed_roles,
        )
        return document

    return _dependency


def _get_job_for_access(db: Session, job_id: UUID) -> ProcessingJob:
    job = ProcessingJobRepository.get_by_id(db, job_id)
    if job is None:
        raise AppException(
            message="Job not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="JOB_NOT_FOUND",
        )
    return job


def job_access_dependency(*, allowed_roles: set[str] | None = None) -> Callable[..., ProcessingJob]:
    def _dependency(
        job_id: UUID,
        db: DbSession,
        current_user: CurrentUser,
    ) -> ProcessingJob:
        job = _get_job_for_access(db, job_id)
        require_workspace_access(
            job.workspace_id,
            db=db,
            current_user=current_user,
            allowed_roles=allowed_roles,
        )
        return job

    return _dependency


def _get_risk_finding_for_access(db: Session, finding_id: UUID) -> RiskFinding:
    finding = RiskFindingRepository.get_by_id(db, finding_id)
    if finding is None:
        raise AppException(
            message="Risk finding not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=RISK_FINDING_NOT_FOUND,
        )
    return finding


def risk_finding_access_dependency(
    *,
    allowed_roles: set[str] | None = None,
) -> Callable[..., RiskFinding]:
    def _dependency(
        finding_id: UUID,
        db: DbSession,
        current_user: CurrentUser,
    ) -> RiskFinding:
        finding = _get_risk_finding_for_access(db, finding_id)
        require_workspace_access(
            finding.workspace_id,
            db=db,
            current_user=current_user,
            allowed_roles=allowed_roles,
        )
        return finding

    return _dependency


def _get_risk_rule_config_for_access(db: Session, config_id: UUID) -> RiskRuleConfig:
    config = RiskRuleConfigRepository.get_by_id(db, config_id)
    if config is None:
        raise AppException(
            message="Risk rule config not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=RISK_RULE_CONFIG_NOT_FOUND,
        )
    return config


def risk_rule_config_access_dependency(
    *,
    allowed_roles: set[str] | None = None,
) -> Callable[..., RiskRuleConfig]:
    def _dependency(
        config_id: UUID,
        db: DbSession,
        current_user: CurrentUser,
    ) -> RiskRuleConfig:
        config = _get_risk_rule_config_for_access(db, config_id)
        require_workspace_access(
            config.workspace_id,
            db=db,
            current_user=current_user,
            allowed_roles=allowed_roles,
        )
        return config

    return _dependency
