from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    @staticmethod
    def create(
        db: Session,
        *,
        email: str,
        hashed_password: str,
        full_name: str | None = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> User | None:
        return db.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        normalized_email = email.strip().lower()
        return db.scalar(select(User).where(User.email == normalized_email))
