from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    @staticmethod
    def create_client(db: Session, payload: ClientCreate) -> Client:
        return ClientRepository.create(db, payload)

    @staticmethod
    def list_clients(db: Session) -> list[Client]:
        return ClientRepository.get_all(db)

    @staticmethod
    def get_client(db: Session, client_id: UUID) -> Client:
        client = ClientRepository.get_by_id(db, client_id)
        if client is None:
            raise AppException(
                message="Client not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="CLIENT_NOT_FOUND",
            )
        return client

    @staticmethod
    def update_client(db: Session, client_id: UUID, payload: ClientUpdate) -> Client:
        client = ClientService.get_client(db, client_id)
        return ClientRepository.update(db, client, payload)

    @staticmethod
    def deactivate_client(db: Session, client_id: UUID) -> Client:
        client = ClientService.get_client(db, client_id)
        return ClientRepository.deactivate(db, client)
