from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import STATUS_INACTIVE
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


class ClientRepository:
    @staticmethod
    def create(db: Session, payload: ClientCreate) -> Client:
        client = Client(**payload.model_dump())
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def get_by_id(db: Session, client_id: UUID) -> Client | None:
        return db.scalar(select(Client).where(Client.id == client_id))

    @staticmethod
    def get_all(db: Session) -> list[Client]:
        return list(db.scalars(select(Client).order_by(Client.created_at.desc())))

    @staticmethod
    def update(db: Session, client: Client, payload: ClientUpdate) -> Client:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def deactivate(db: Session, client: Client) -> Client:
        client.status = STATUS_INACTIVE
        db.commit()
        db.refresh(client)
        return client
