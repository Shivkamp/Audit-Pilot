from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, require_active_user
from app.core.responses import success_response
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.services.client_service import ClientService

# TODO: Client routes are not scoped by ownership — any authenticated user can read or
# modify any client. Implement per-user client ownership before multi-tenant production use.
router = APIRouter(dependencies=[Depends(require_active_user)])


def _serialize_client(client: object) -> dict:
    return ClientResponse.model_validate(client).model_dump(mode="json")


@router.post("")
def create_client(payload: ClientCreate, db: DbSession) -> dict:
    client = ClientService.create_client(db, payload)
    return success_response(
        message="Client created successfully.",
        data=_serialize_client(client),
    )


@router.get("")
def list_clients(db: DbSession) -> dict:
    clients = ClientService.list_clients(db)
    return success_response(
        message="Clients fetched successfully.",
        data=[_serialize_client(client) for client in clients],
    )


@router.get("/{client_id}")
def get_client(client_id: UUID, db: DbSession) -> dict:
    client = ClientService.get_client(db, client_id)
    return success_response(
        message="Client fetched successfully.",
        data=_serialize_client(client),
    )


@router.patch("/{client_id}")
def update_client(client_id: UUID, payload: ClientUpdate, db: DbSession) -> dict:
    client = ClientService.update_client(db, client_id, payload)
    return success_response(
        message="Client updated successfully.",
        data=_serialize_client(client),
    )


@router.delete("/{client_id}")
def deactivate_client(client_id: UUID, db: DbSession) -> dict:
    client = ClientService.deactivate_client(db, client_id)
    return success_response(
        message="Client deactivated successfully.",
        data=_serialize_client(client),
    )
