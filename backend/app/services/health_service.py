from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import AppException


class HealthService:
    @staticmethod
    def check_database(db: Session) -> None:
        try:
            db.execute(text("SELECT 1"))
        except Exception as exc:  # pragma: no cover - depends on db availability
            raise AppException(
                message="Database health check failed.",
                status_code=503,
                error_code="database_unavailable",
            ) from exc
