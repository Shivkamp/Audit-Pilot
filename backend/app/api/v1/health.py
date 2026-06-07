from fastapi import APIRouter

from app.api.deps import DbSession
from app.core.config import settings
from app.core.responses import success_response
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict:
    return success_response(
        message="Service is healthy.",
        data={"status": "ok", "service": settings.project_name},
    )


@router.get("/health/db")
def health_db_check(db: DbSession) -> dict:
    HealthService.check_database(db)
    return success_response(
        message="Database connection healthy.",
        data={"status": "ok", "database": "postgresql"},
    )
