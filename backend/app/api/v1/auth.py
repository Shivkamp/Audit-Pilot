from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.schemas.auth import AuthLoginRequest, AuthRegisterRequest, AuthTokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


def _serialize_user(user: object) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post("/register")
def register_user(payload: AuthRegisterRequest, db: DbSession) -> dict:
    user = AuthService.register_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    access_token = AuthService.create_access_token(user)
    response_data = AuthTokenResponse(
        access_token=access_token,
        user=_serialize_user(user),
    )
    return success_response(
        message="User registered successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.post("/login")
def login_user(payload: AuthLoginRequest, db: DbSession) -> dict:
    user = AuthService.authenticate_user(
        db,
        email=payload.email,
        password=payload.password,
    )
    access_token = AuthService.create_access_token(user)
    response_data = AuthTokenResponse(
        access_token=access_token,
        user=_serialize_user(user),
    )
    return success_response(
        message="Login successful.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/me")
def get_current_user_profile(current_user: CurrentUser) -> dict:
    return success_response(
        message="User profile fetched successfully.",
        data=_serialize_user(current_user).model_dump(mode="json"),
    )
