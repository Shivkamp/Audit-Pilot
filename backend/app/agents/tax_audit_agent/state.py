from __future__ import annotations

from typing import Any, TypedDict


class TaxAuditAgentState(TypedDict, total=False):
    workspace_id: str
    user_message: str
    intent: str
    intent_confidence: float
    risk_summary: dict[str, Any] | None
    risk_findings: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    source_traces: list[dict[str, Any]]
    answer: str
    citations: list[dict[str, Any]]
    warnings: list[str]
    errors: list[str]
    include_evidence: bool
    include_source_trace: bool
    max_evidence: int
    provider: str | None
    model: str | None
