from sqlalchemy.engine import Engine

from app.models.base import Base


def init_db(engine: Engine) -> None:
    """Initialize database tables.

    Prefer Alembic migrations (``alembic upgrade head``) for schema changes;
    ``Base.metadata.create_all`` is only a minimal bootstrap fallback.
    """

    Base.metadata.create_all(bind=engine)
