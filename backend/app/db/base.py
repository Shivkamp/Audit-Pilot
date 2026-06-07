"""Database metadata registry for Alembic autogeneration."""

from app.models.base import Base
from app.models.client import Client  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.extracted_record import ExtractedRecord  # noqa: F401
from app.models.knowledge_chunk import KnowledgeChunk  # noqa: F401
from app.models.normalized_record import NormalizedRecord  # noqa: F401
from app.models.processing_job import ProcessingJob  # noqa: F401
from app.models.risk_finding import RiskFinding  # noqa: F401
from app.models.risk_rule_config import RiskRuleConfig  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401
from app.models.workspace_member import WorkspaceMember  # noqa: F401

# SQLAlchemy models must be imported here for Alembic autogeneration.
