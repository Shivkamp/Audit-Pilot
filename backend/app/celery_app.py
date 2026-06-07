from celery import Celery

from app.core.config import settings

# ---------------------------------------------------------------------------
# Redis 5.x compatibility (Windows)
#
# redis-py >= 8.0 ships with DEFAULT_RESP_VERSION = 3, meaning any connection
# created without an explicit `protocol` argument defaults to RESP3 and sends
# "HELLO 3" on handshake.  Redis < 6 does not implement HELLO, so the
# connection fails.  Changing DEFAULT_RESP_VERSION to 2 here (before Celery /
# kombu import their transport classes) makes every connection default to
# RESP2, which disables HELLO and the Redis-8-only maintenance-notifications
# feature that redis-py 8 auto-enables when protocol == 3.
# ---------------------------------------------------------------------------
try:
    import redis.utils as _redis_utils
    import redis.connection as _redis_connection

    # redis.utils.DEFAULT_RESP_VERSION is read by check_protocol_version()
    # which the ConnectionPool uses to decide whether to enable maintenance
    # notifications (a Redis-8 / RESP3 feature).
    _redis_utils.DEFAULT_RESP_VERSION = 2
    # redis.connection.DEFAULT_RESP_VERSION is the fallback used inside
    # AbstractConnection.__init__ when protocol=None → int(None) → TypeError.
    _redis_connection.DEFAULT_RESP_VERSION = 2
except Exception:  # pragma: no cover
    pass  # If redis-py changes its internals this is a no-op rather than a crash
# ---------------------------------------------------------------------------

celery_app = Celery(
    "taxaudit_ai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.document_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
