from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.tax_audit_agent.graph import build_tax_audit_agent_graph
from app.agents.tax_audit_agent.intents import INTENT_UNSUPPORTED
from app.agents.tax_audit_agent.state import TaxAuditAgentState
from app.agents.tax_audit_agent.tools import TaxAuditAgentTools
from app.core.config import settings
from app.core.constants import AGENT_CHAT_FAILED
from app.core.exceptions import AppException
from app.core.logging import logger
from app.llm.service import LLMService
from app.schemas.agent_chat import AgentChatRequest


class AgentChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.tools = TaxAuditAgentTools(db)
        self.llm_service = LLMService()
        self.graph = build_tax_audit_agent_graph(
            tools=self.tools,
            llm_service=self.llm_service,
        )

    def chat_workspace(self, workspace_id: UUID, payload: AgentChatRequest) -> dict[str, Any]:
        try:
            initial_state: TaxAuditAgentState = {
                "workspace_id": str(workspace_id),
                "user_message": payload.message,
                "intent": INTENT_UNSUPPORTED,
                "intent_confidence": 0.0,
                "risk_summary": None,
                "risk_findings": [],
                "evidence": [],
                "source_traces": [],
                "answer": "",
                "citations": [],
                "warnings": [],
                "errors": [],
                "include_evidence": bool(payload.include_evidence),
                "include_source_trace": bool(payload.include_source_trace),
                "max_evidence": int(payload.max_evidence),
                "provider": None,
                "model": None,
            }

            final_state = self.graph.invoke(initial_state)
            return self._build_response(payload, final_state)
        except AppException:
            raise
        except Exception as exc:
            logger.exception("Agent chat execution failed for workspace_id=%s", workspace_id)
            raise AppException(
                message="Agent chat request failed due to an internal processing error.",
                status_code=500,
                error_code=AGENT_CHAT_FAILED,
            ) from exc

    def _build_response(self, payload: AgentChatRequest, final_state: dict[str, Any]) -> dict[str, Any]:
        warnings = [
            warning
            for warning in (final_state.get("warnings") or [])
            if isinstance(warning, str) and warning.strip()
        ]
        warnings = [warning for warning in dict.fromkeys(warnings)]

        intent = str(final_state.get("intent") or INTENT_UNSUPPORTED)
        confidence = self._build_confidence_label(
            intent=intent,
            intent_confidence=float(final_state.get("intent_confidence") or 0.0),
            warnings=warnings,
            citations=final_state.get("citations") or [],
        )

        source_traces = final_state.get("source_traces") or []
        if not payload.include_source_trace:
            source_traces = []

        evidence = final_state.get("evidence") or []
        if not payload.include_evidence:
            evidence = []

        workspace_text = str(final_state.get("workspace_id") or "")

        return {
            "workspace_id": workspace_text,
            "message": payload.message,
            "intent": intent,
            "answer": str(final_state.get("answer") or ""),
            "citations": final_state.get("citations") or [],
            "evidence": evidence,
            "source_traces": source_traces,
            "warnings": warnings,
            "confidence": confidence,
            "provider": final_state.get("provider"),
            "model": final_state.get("model"),
        }

    def _build_confidence_label(
        self,
        *,
        intent: str,
        intent_confidence: float,
        warnings: list[str],
        citations: list[dict[str, Any]],
    ) -> str:
        if intent == INTENT_UNSUPPORTED:
            return "low"

        score = max(0.0, min(1.0, float(intent_confidence)))
        if warnings:
            score -= min(0.25, 0.05 * len(warnings))

        if settings.agent_require_citations and not citations:
            score -= 0.2

        if score >= 0.85:
            return "high"
        if score >= 0.60:
            return "medium"
        return "low"
