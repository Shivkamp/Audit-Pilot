from __future__ import annotations

from datetime import timedelta
from functools import cache
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    AUTH_FORBIDDEN,
    AUTH_INACTIVE_USER,
    AUTH_INVALID_CREDENTIALS,
    AUTH_TOKEN_INVALID,
    USER_EMAIL_ALREADY_EXISTS,
)
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token as security_create_access_token,
    decode_access_token,
    hash_password as security_hash_password,
    verify_password as security_verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository


@cache
def _dummy_hash() -> str:
    """Bcrypt hash computed once on first use; prevents timing-based email enumeration."""
    return security_hash_password("__auth_service_dummy_verify__")


class AuthService:
    @staticmethod
    def register_user(
        db: Session,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> User:
        if not settings.allow_public_registration:
            raise AppException(
                message="Public registration is disabled.",
                status_code=status.HTTP_403_FORBIDDEN,
                error_code=AUTH_FORBIDDEN,
            )

        normalized_email = email.strip().lower()
        existing_user = UserRepository.get_by_email(db, normalized_email)
        if existing_user is not None:
            raise AppException(
                message="Email is already registered.",
                status_code=status.HTTP_409_CONFLICT,
                error_code=USER_EMAIL_ALREADY_EXISTS,
            )

        return UserRepository.create(
            db,
            email=normalized_email,
            hashed_password=AuthService.hash_password(password),
            full_name=(full_name or None),
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        *,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()
        user = UserRepository.get_by_email(db, normalized_email)

        if user is None:
            # Always run bcrypt to prevent timing-based email enumeration.
            security_verify_password(password, _dummy_hash())
            raise AppException(
                message="Invalid email or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code=AUTH_INVALID_CREDENTIALS,
            )

        if not AuthService.verify_password(password, user.hashed_password):
            raise AppException(
                message="Invalid email or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code=AUTH_INVALID_CREDENTIALS,
            )

        if not user.is_active:
            raise AppException(
                message="User account is inactive.",
                status_code=status.HTTP_403_FORBIDDEN,
                error_code=AUTH_INACTIVE_USER,
            )

        return user

    @staticmethod
    def create_access_token(user: User) -> str:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        return security_create_access_token(
            subject=str(user.id),
            email=user.email,
            expires_delta=expires_delta,
        )

    @staticmethod
    def get_current_user_from_token(db: Session, token: str) -> User:
        payload = decode_access_token(token)
        user_id_raw = payload.get("sub")

        try:
            user_id = UUID(str(user_id_raw))
        except (TypeError, ValueError) as exc:
            raise AppException(
                message="Authentication token is invalid.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code=AUTH_TOKEN_INVALID,
            ) from exc

        user = UserRepository.get_by_id(db, user_id)
        if user is None:
            raise AppException(
                message="Authentication token is invalid.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code=AUTH_TOKEN_INVALID,
            )

        if not user.is_active:
            raise AppException(
                message="User account is inactive.",
                status_code=status.HTTP_403_FORBIDDEN,
                error_code=AUTH_INACTIVE_USER,
            )

        return user

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return security_verify_password(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return security_hash_password(password)
