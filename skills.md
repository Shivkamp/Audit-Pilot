# skills.md — Agent Guidelines for TaxAudit AI Backend

## Project Context

You are working on **TaxAudit AI**, a production-style FastAPI backend for an AI Audit / Tax Intelligence Platform.

The platform will eventually support:

- Client and workspace management
- Document upload
- Async document processing with Celery
- PDF/Excel extraction
- Financial/tax data normalization
- Risk detection
- RAG-based chatbot with citations
- Dashboard APIs
- Report generation

Current implemented modules:

- Module 1: Backend Foundation
- Module 2: Database Foundation
- Module 3: Client + Workspace Module

Do not build future modules unless explicitly asked.

---

## Core Architecture Rules

Use the layered architecture consistently:

```text
API route → Service → Repository → Database
```

### API Layer

Location:

```text
app/api/v1/
```

Responsibilities:

- Define HTTP endpoints
- Accept request schemas
- Inject DB session using `Depends(get_db)`
- Call service methods
- Return response schemas or response helpers

Routes should **not** contain:

- SQLAlchemy queries
- business validation logic
- direct commits
- complex transformation logic

---

### Service Layer

Location:

```text
app/services/
```

Responsibilities:

- Business rules
- Validation
- Entity existence checks
- Raising `AppException`
- Calling repositories
- Coordinating multiple repositories if needed

Example:

```text
WorkspaceService.create_workspace()
  ↓
checks client exists
  ↓
creates workspace using WorkspaceRepository
```

---

### Repository Layer

Location:

```text
app/repositories/
```

Responsibilities:

- Database reads/writes only
- SQLAlchemy queries
- Add/update records
- Commit and refresh if the project pattern already does so

Repositories should **not**:

- raise HTTPException
- know about API responses
- contain business decisions

---

### Models Layer

Location:

```text
app/models/
```

Responsibilities:

- SQLAlchemy ORM table definitions
- Relationships
- Foreign keys

Use SQLAlchemy 2.0 style where possible:

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
```

All business models should inherit from existing base/mixins:

```python
Base
UUIDMixin
TimestampMixin
```

---

### Schemas Layer

Location:

```text
app/schemas/
```

Responsibilities:

- Pydantic request and response models
- Separate create/update/response schemas

For response schemas from SQLAlchemy models, use:

```python
from pydantic import ConfigDict

model_config = ConfigDict(from_attributes=True)
```

---

## Existing Core Components To Reuse

### `AppException`

Location:

```text
app/core/exceptions.py
```

Use `AppException` for controlled application errors.

Example:

```python
raise AppException(
    message="Client not found",
    status_code=404,
    error_code="CLIENT_NOT_FOUND",
)
```

Do not raise raw `HTTPException` from services/repositories unless the existing project pattern explicitly requires it.

---

### Success Response Helper

Location:

```text
app/utils/response.py
```

Use existing helper if available, likely similar to:

```python
def success_response(message: str, data=None):
    return {
        "success": True,
        "message": message,
        "data": data,
    }
```

Use it when returning generic success payloads.

For typed CRUD APIs, prefer returning Pydantic response schemas directly if that is already the route pattern.

---

### Error Response Helper

Location:

```text
app/utils/response.py
```

Use existing helper if available, likely similar to:

```python
def error_response(message: str, error_code: str | None = None):
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
    }
```

Most controlled errors should flow through `AppException` and global exception handlers instead of manually returning error responses everywhere.

---

### Status Constants

Location:

```text
app/core/constants.py
```

Use existing constants instead of hardcoding repeated strings:

```python
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_ARCHIVED = "archived"
```

Rules:

- Client delete should deactivate: `status = STATUS_INACTIVE`
- Workspace delete should archive: `status = STATUS_ARCHIVED`
- Active listing should generally filter by `STATUS_ACTIVE`, unless the endpoint explicitly needs all statuses

---

### DB Session

Location:

```text
app/db/session.py
```

Use:

```python
db: Session = Depends(get_db)
```

Do not manually create sessions inside routes.

---

### Alembic Model Discovery

Location:

```text
app/db/base.py
```

Whenever a new SQLAlchemy model is added, import it in `app/db/base.py` so Alembic can detect it.

Example:

```python
from app.models.client import Client
from app.models.workspace import Workspace
```

If Alembic says `No changes detected`, first check this file.

---

## Current Implemented Domain

### Client

A client is the company/entity being reviewed.

Example:

```text
ABC Consulting Pvt Ltd
```

Existing expected fields:

```text
id
name
pan
gstin
tan
email
phone
address
industry
status
created_at
updated_at
```

---

### Workspace

A workspace is a review/project under a client.

Example:

```text
TDS Review FY 2024-25
```

Existing expected fields:

```text
id
client_id
name
description
financial_year
status
created_at
updated_at
```

Hierarchy:

```text
Client
  └── Workspace
        └── Future Documents
              └── Future Risks
                    └── Future Reports
```

---

## Existing API Expectations

### Health

```text
GET /api/v1/health
GET /api/v1/health/db
```

---

### Clients

```text
POST   /api/v1/clients
GET    /api/v1/clients
GET    /api/v1/clients/{client_id}
PATCH  /api/v1/clients/{client_id}
DELETE /api/v1/clients/{client_id}
```

Delete should not hard-delete. It should set status to inactive.

---

### Workspaces

```text
POST   /api/v1/clients/{client_id}/workspaces
GET    /api/v1/clients/{client_id}/workspaces
GET    /api/v1/workspaces/{workspace_id}
PATCH  /api/v1/workspaces/{workspace_id}
DELETE /api/v1/workspaces/{workspace_id}
```

Delete should not hard-delete. It should set status to archived.

---

## Error Handling Rules

Use consistent error codes.

Existing important error codes:

```text
CLIENT_NOT_FOUND
WORKSPACE_NOT_FOUND
APP_ERROR
```

Example error payload should look like:

```json
{
  "success": false,
  "message": "Client not found",
  "error_code": "CLIENT_NOT_FOUND"
}
```

Do not leak raw stack traces in API responses.

---

## Coding Style Guidelines

### Keep routes thin

Bad:

```python
@router.get("/{client_id}")
def get_client(client_id, db):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(404)
    return client
```

Good:

```python
@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: UUID, db: Session = Depends(get_db)):
    return ClientService.get_client(db, client_id)
```

---

### Keep services business-focused

Services should answer business questions like:

- Does this client exist?
- Is this workspace allowed under this client?
- Should this delete be soft-delete instead of hard-delete?

---

### Keep repositories DB-focused

Repositories should answer database questions like:

- Fetch by ID
- Insert row
- Update row
- List active rows

---

## Migration Rules

After adding or changing models:

```bash
alembic revision --autogenerate -m "meaningful migration message"
alembic upgrade head
```

Before generating migration, ensure:

- New models are imported in `app/db/base.py`
- `target_metadata = Base.metadata` is configured in `alembic/env.py`
- DB is running

---

## What Not To Do Without Explicit Instruction

Do not add these unless the user asks for the relevant module:

```text
Document upload
Celery
Redis
PDF parsing
Excel parsing
RAG
Vector DB
Chatbot
Risk engine
Dashboard
Reports
Authentication
Role-based access
Cloud storage
```

Do not refactor verified foundation files unless necessary for the current task.

---

## Future Module Awareness

### Module 4 will likely be Document Upload

Documents should belong to a workspace, not directly to a client.

Expected future route shape:

```text
POST /api/v1/workspaces/{workspace_id}/documents/upload
```

Future Document model will likely include:

```text
id
workspace_id
original_filename
stored_filename
file_path
file_type
mime_type
file_size
status
created_at
updated_at
```

### Module 5 will likely be Celery + Job Tracking

Async processing should be used for heavy tasks:

```text
PDF extraction
Excel parsing
OCR
Embedding generation
Risk checks
Report generation
```

---

## Agent Behavior Instructions

When implementing a module:

1. Modify only files relevant to the module.
2. Do not rewrite already verified files unnecessarily.
3. Preserve existing route prefixes.
4. Preserve existing response/error patterns.
5. Use existing constants/helpers/exceptions.
6. Add models to `app/db/base.py` for Alembic.
7. Keep API → Service → Repository separation.
8. Add tests only if the test setup already exists or the user asks.
9. Do not add future-module dependencies early.
10. Prefer small, reviewable changes.

---

## Quick Sanity Checklist Before Finishing Any Module

- Does `uvicorn app.main:app --reload` start?
- Does Swagger open at `/docs`?
- Do existing health endpoints still work?
- Does Alembic detect new model changes?
- Do routes avoid direct DB logic?
- Do services raise `AppException` for controlled errors?
- Are constants reused instead of hardcoded statuses?
- Are response schemas using `from_attributes=True` where needed?
- Are deletes soft-delete/archive where auditability matters?
- Did you avoid adding unrelated future functionality?
