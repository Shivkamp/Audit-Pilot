from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.agent_chat import router as agent_chat_router
from app.api.v1.classification import router as classification_router
from app.api.v1.clients import router as clients_router
from app.api.v1.agent_retrieval import router as agent_retrieval_router
from app.api.v1.documents import router as documents_router
from app.api.v1.extraction import router as extraction_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.normalization import router as normalization_router
from app.api.v1.risks import router as risks_router
from app.api.v1.risk_rule_configs import router as risk_rule_configs_router
from app.api.v1.workspaces import router as workspaces_router
from app.api.v1.workspace_members import router as workspace_members_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(clients_router, prefix="/clients", tags=["Clients"])
api_router.include_router(workspaces_router, tags=["Workspaces"])
api_router.include_router(workspace_members_router, tags=["Workspace Members"])
api_router.include_router(documents_router, tags=["Documents"])
api_router.include_router(jobs_router, tags=["Jobs"])
api_router.include_router(extraction_router, tags=["Extraction"])
api_router.include_router(classification_router, tags=["Classification"])
api_router.include_router(normalization_router, tags=["Normalization"])
api_router.include_router(risks_router, tags=["Risks"])
api_router.include_router(risk_rule_configs_router, tags=["Risk Rule Configs"])
api_router.include_router(knowledge_router, tags=["Knowledge"])
api_router.include_router(agent_retrieval_router, tags=["Agent Retrieval"])
api_router.include_router(agent_chat_router, tags=["Agent Chat"])
