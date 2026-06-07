from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi import status
from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings
from app.core.constants import AUTH_TOKEN_EXPIRED, AUTH_TOKEN_INVALID
from app.core.exceptions import AppException

_DEV_SECRET_PLACEHOLDERS = {
    "",
    "change-me-dev-secret",
    "replace-me-in-production",
}


def _ensure_secret_key_is_safe_for_environment() -> None:
    secret_key = (settings.auth_secret_key or "").strip()
    if settings.is_development:
        return

    if secret_key in _DEV_SECRET_PLACEHOLDERS:
        raise RuntimeError(
            "AUTH_SECRET_KEY must be configured with a non-placeholder value in non-development environments."
        )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(
    *,
    subject: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    _ensure_secret_key_is_safe_for_environment()

    issued_at = datetime.now(UTC)
    expire_at = issued_at + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))

    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "iat": int(issued_at.timestamp()),
        "exp": int(expire_at.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    _ensure_secret_key_is_safe_for_environment()

    try:
        payload = jwt.decode(
            token,
            settings.auth_secret_key,
            algorithms=[settings.auth_algorithm],
        )
    except ExpiredSignatureError as exc:
        raise AppException(
            message="Authentication token has expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=AUTH_TOKEN_EXPIRED,
        ) from exc
    except JWTError as exc:
        raise AppException(
            message="Authentication token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=AUTH_TOKEN_INVALID,
        ) from exc

    if not payload.get("sub"):
        raise AppException(
            message="Authentication token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=AUTH_TOKEN_INVALID,
        )

    return payload
