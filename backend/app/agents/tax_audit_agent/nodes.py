from __future__ import annotations

import re
from typing import Any

from fastapi import status

from app.agents.tax_audit_agent.citations import (
    attach_best_available_citations,
    collect_available_citations,
    keep_only_valid_citations,
)
from app.agents.tax_audit_agent.intents import (
    INTENT_EVIDENCE_SEARCH,
    INTENT_RISK_EXPLANATION,
    INTENT_RISK_LISTING,
    INTENT_RISK_SUMMARY,
    INTENT_SOURCE_TRACE,
    INTENT_UNSUPPORTED,
    classify_intent,
)
from app.agents.tax_audit_agent.prompts import build_grounded_answer_messages
from app.agents.tax_audit_agent.state import TaxAuditAgentState
from app.agents.tax_audit_agent.tools import TaxAuditAgentTools
from app.core.config import settings
from app.core.constants import AGENT_CHAT_MESSAGE_REQUIRED, KNOWLEDGE_SOURCE_TYPE_RISK_FINDING
from app.core.exceptions import AppException
from app.llm.service import LLMService

_FACTUAL_INTENTS = {
    INTENT_RISK_SUMMARY,
    INTENT_RISK_LISTING,
    INTENT_RISK_EXPLANATION,
    INTENT_EVIDENCE_SEARCH,
    INTENT_SOURCE_TRACE,
}


def validate_request_node(
    state: TaxAuditAgentState,
    *,
    tools: TaxAuditAgentTools,
) -> dict[str, Any]:
    message = (state.get("user_message") or "").strip()
    if not message:
        raise AppException(
            message="Message cannot be blank.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=AGENT_CHAT_MESSAGE_REQUIRED,
        )

    workspace_id = str(state.get("workspace_id") or "").strip()
    readiness = tools.check_workspace_ready(workspace_id)

    max_limit = min(int(settings.agent_max_evidence), int(settings.agent_retrieval_max_limit))
    requested_max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)
    clamped_max_evidence = max(1, min(requested_max_evidence, max_limit))

    warnings = list(state.get("warnings") or [])
    if not readiness.get("ready"):
        warnings.append("No risk findings found. Run risk check first.")

    return {
        "workspace_id": str(readiness["workspace_id"]),
        "user_message": message,
        "warnings": _dedupe_strings(warnings),
        "errors": list(state.get("errors") or []),
        "include_evidence": bool(state.get("include_evidence", True)),
        "include_source_trace": bool(state.get("include_source_trace", True)),
        "max_evidence": clamped_max_evidence,
        "risk_summary": state.get("risk_summary"),
        "risk_findings": list(state.get("risk_findings") or []),
        "evidence": list(state.get("evidence") or []),
        "source_traces": list(state.get("source_traces") or []),
        "citations": list(state.get("citations") or []),
        "answer": str(state.get("answer") or ""),
    }


def classify_intent_node(
    state: TaxAuditAgentState,
    *,
    llm_service: LLMService,
) -> dict[str, Any]:
    intent, confidence = classify_intent(state.get("user_message") or "", llm_service=llm_service)
    return {
        "intent": intent,
        "intent_confidence": float(confidence),
    }


def risk_summary_node(
    state: TaxAuditAgentState,
    *,
    tools: TaxAuditAgentTools,
) -> dict[str, Any]:
    max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)
    include_evidence = bool(state.get("include_evidence", True))
    include_source_trace = bool(state.get("include_source_trace", True))

    summary_data = tools.get_risk_summary(state["workspace_id"], limit=max_evidence)
    risk_summary = summary_data.get("risk_summary") if isinstance(summary_data, dict) else None
    risk_findings = summary_data.get("risk_findings") if isinstance(summary_data, dict) else []
    risk_findings = risk_findings if isinstance(risk_findings, list) else []

    warnings = list(state.get("warnings") or [])
    total_findings = int((risk_summary or {}).get("total_findings") or 0)
    if total_findings <= 0:
        warnings.append("No risk findings found. Run risk check first.")

    evidence: list[dict[str, Any]] = []
    if include_evidence:
        counts_by_risk_type = (risk_summary or {}).get("counts_by_risk_type") or {}
        ranked_risk_types = []
        if isinstance(counts_by_risk_type, dict):
            ranked_risk_types = [
                risk_type
                for risk_type, _ in sorted(
                    counts_by_risk_type.items(),
                    key=lambda item: (-int(item[1]), str(item[0])),
                )
            ]

        # Cap to top 3 risk types: each loop iteration runs a full semantic search
        # (vector embedding + RRF + MMR), so iterating over all 8 risk types serially
        # can add several seconds before the LLM generation step even starts.
        _MAX_RISK_TYPE_SEARCHES = 3
        for risk_type in ranked_risk_types[:_MAX_RISK_TYPE_SEARCHES]:
            remaining = max_evidence - len(evidence)
            if remaining <= 0:
                break
            risk_evidence_payload = tools.retrieve_risk_evidence(
                state["workspace_id"],
                query=state["user_message"],
                limit=remaining,
                include_source_trace=include_source_trace,
                risk_type=risk_type,
            )
            evidence.extend(_ensure_list_of_dicts(risk_evidence_payload.get("evidence")))

        if not evidence and state.get("user_message"):
            workspace_evidence_payload = tools.retrieve_workspace_evidence(
                state["workspace_id"],
                query=state["user_message"],
                limit=max_evidence,
                include_source_trace=include_source_trace,
            )
            evidence = _ensure_list_of_dicts(workspace_evidence_payload.get("evidence"))

    evidence = _dedupe_evidence(evidence)[:max_evidence]
    source_traces = _extract_source_traces(evidence, include_source_trace=include_source_trace)

    return {
        "risk_summary": risk_summary,
        "risk_findings": risk_findings,
        "evidence": evidence,
        "source_traces": source_traces,
        "warnings": _dedupe_strings(warnings),
    }


def risk_listing_node(
    state: TaxAuditAgentState,
    *,
    tools: TaxAuditAgentTools,
) -> dict[str, Any]:
    max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)
    include_evidence = bool(state.get("include_evidence", True))
    include_source_trace = bool(state.get("include_source_trace", True))

    inferred_risk_type = tools.infer_risk_type_from_text(state["user_message"])
    findings_payload = tools.list_risk_findings(
        state["workspace_id"],
        risk_type=inferred_risk_type,
        severity=None,
        status_filter=None,
        limit=int(settings.agent_listing_max_limit),
        offset=0,
    )

    risk_findings = _ensure_list_of_dicts(findings_payload.get("findings"))
    evidence: list[dict[str, Any]] = []
    if include_evidence:
        evidence_payload = tools.retrieve_workspace_evidence(
            state["workspace_id"],
            query=state["user_message"],
            limit=max_evidence,
            include_source_trace=include_source_trace,
        )
        evidence = _ensure_list_of_dicts(evidence_payload.get("evidence"))

    warnings = list(state.get("warnings") or [])
    if not risk_findings:
        warnings.append("No risk findings matched your listing request.")

    return {
        "risk_findings": risk_findings,
        "evidence": _dedupe_evidence(evidence)[:max_evidence],
        "source_traces": _extract_source_traces(evidence, include_source_trace=include_source_trace),
        "warnings": _dedupe_strings(warnings),
    }


def risk_explanation_node(
    state: TaxAuditAgentState,
    *,
    tools: TaxAuditAgentTools,
) -> dict[str, Any]:
    max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)
    include_source_trace = bool(state.get("include_source_trace", True))

    inferred_risk_type = tools.infer_risk_type_from_text(state["user_message"])

    evidence_payload = tools.retrieve_risk_evidence(
        state["workspace_id"],
        query=state["user_message"],
        limit=max_evidence,
        include_source_trace=include_source_trace,
        risk_type=inferred_risk_type,
    )
    evidence = _ensure_list_of_dicts(evidence_payload.get("evidence"))

    findings_payload = tools.list_risk_findings(
        state["workspace_id"],
        risk_type=inferred_risk_type,
        severity=None,
        status_filter=None,
        limit=int(settings.agent_retrieval_max_limit),
        offset=0,
    )
    risk_findings = _ensure_list_of_dicts(findings_payload.get("findings"))

    warnings = list(state.get("warnings") or [])
    if not evidence:
        warnings.append("No direct evidence was found for this explanation request.")

    return {
        "risk_findings": risk_findings,
        "evidence": _dedupe_evidence(evidence)[:max_evidence],
        "source_traces": _extract_source_traces(evidence, include_source_trace=include_source_trace),
        "warnings": _dedupe_strings(warnings),
    }


def evidence_search_node(
    state: TaxAuditAgentState,
    *,
    tools: TaxAuditAgentTools,
) -> dict[str, Any]:
    max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)
    include_source_trace = bool(state.get("include_source_trace", True))

    evidence_payload = tools.retrieve_workspace_evidence(
        state["workspace_id"],
        query=state["user_message"],
        limit=max_evidence,
        include_source_trace=include_source_trace,
    )
    evidence = _ensure_list_of_dicts(evidence_payload.get("evidence"))

    warnings = list(state.get("warnings") or [])
    if not evidence:
        warnings.append("No evidence matched this search query.")

    return {
        "evidence": _dedupe_evidence(evidence)[:max_evidence],
        "source_traces": _extract_source_traces(evidence, include_source_trace=include_source_trace),
        "warnings": _dedupe_strings(warnings),
    }


def source_trace_node(
    state: TaxAuditAgentState,
    *,
    tools: TaxAuditAgentTools,
) -> dict[str, Any]:
    include_source_trace = bool(state.get("include_source_trace", True))
    max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)

    source_type, source_id = _extract_source_reference(state["user_message"])
    source_traces: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    warnings = list(state.get("warnings") or [])

    if source_type and source_id:
        try:
            source_traces.append(
                tools.get_source_trace(
                    state["workspace_id"],
                    source_type=source_type,
                    source_id=source_id,
                )
            )
        except AppException:
            warnings.append("Requested source trace could not be resolved directly; fallback evidence was used.")

    if not source_traces:
        evidence_payload = tools.retrieve_workspace_evidence(
            state["workspace_id"],
            query=state["user_message"],
            limit=max_evidence,
            include_source_trace=True,
        )
        evidence = _ensure_list_of_dicts(evidence_payload.get("evidence"))
        source_traces = _extract_source_traces(evidence, include_source_trace=True)

    if include_source_trace and not source_traces:
        warnings.append("No source trace information is available for this request.")

    return {
        "evidence": _dedupe_evidence(evidence)[:max_evidence],
        "source_traces": source_traces[:max_evidence],
        "warnings": _dedupe_strings(warnings),
    }


def unsupported_node(state: TaxAuditAgentState) -> dict[str, Any]:
    warnings = list(state.get("warnings") or [])
    warnings.append(
        "Unsupported question type. Try asking for risk summary, risk listing, explanation, evidence, or source trace."
    )

    return {
        "warnings": _dedupe_strings(warnings),
        "evidence": [],
        "source_traces": [],
        "citations": [],
    }


def generate_grounded_answer_node(
    state: TaxAuditAgentState,
    *,
    llm_service: LLMService,
) -> dict[str, Any]:
    has_findings = bool(state.get("risk_findings"))
    has_evidence = bool(state.get("evidence"))
    has_source_traces = bool(state.get("source_traces"))
    has_summary = bool((state.get("risk_summary") or {}).get("total_findings"))

    if state.get("intent") in _FACTUAL_INTENTS and not (has_findings or has_evidence or has_source_traces or has_summary):
        warnings = list(state.get("warnings") or [])
        warnings.append("Insufficient evidence to provide a grounded factual answer.")
        return {
            "answer": (
                "I don’t have enough processed workspace evidence to answer this confidently yet. "
                "Please run risk checks or refresh indexed evidence, then try again."
            ),
            "warnings": _dedupe_strings(warnings),
        }

    messages = build_grounded_answer_messages(state)
    response = llm_service.generate(
        messages,
        temperature=float(settings.llm_temperature),
        max_tokens=int(settings.llm_max_tokens),
    )

    answer = (response.content or "").strip()
    if not answer:
        # LLM returned empty — build a minimal data-driven fallback so the user
        # still gets something useful when risk findings or evidence are present.
        # NOTE: do NOT re-slice by max_evidence here; the findings list is already
        # correctly sized by the node that populated it (listing nodes use
        # agent_listing_max_limit, not max_evidence).
        findings = state.get("risk_findings") or []
        evidence = state.get("evidence") or []
        if findings:
            lines = [
                "Based on the workspace risk findings:",
            ]
            for f in findings:
                if not isinstance(f, dict):
                    continue
                risk_data = f.get("risk_data") or {}
                vendor = risk_data.get("vendor_name") or risk_data.get("vendor_code") or ""
                title = f.get("title") or f.get("risk_type") or "Unknown risk"
                lines.append(f"- {vendor}: {title} (severity: {f.get('severity', 'unknown')})")  # noqa: E501
            answer = "\n".join(lines)
        elif evidence:
            answer = (
                "Evidence was retrieved but the model could not generate a narrative answer. "
                "Please refine the question or try a more specific query."
            )
        else:
            answer = (
                "I could not generate a grounded answer from the provided data. "
                "Please run a risk check first, then try again."
            )

    return {
        "answer": answer,
        "provider": response.provider,
        "model": response.model,
    }


def validate_citations_node(state: TaxAuditAgentState) -> dict[str, Any]:
    intent = state.get("intent") or INTENT_UNSUPPORTED
    max_evidence = int(state.get("max_evidence") or settings.agent_max_evidence)
    warnings = list(state.get("warnings") or [])

    available_citations = collect_available_citations(state)
    current_citations = _ensure_list_of_dicts(state.get("citations"))
    valid_current = keep_only_valid_citations(current_citations, available_citations)
    final_citations = attach_best_available_citations(valid_current, available_citations, max_evidence)

    if (
        intent in _FACTUAL_INTENTS
        and bool(settings.agent_require_citations)
        and not final_citations
    ):
        warnings.append(
            "Citations are required but no retrievable citation records were found for this response."
        )

    if (
        intent in _FACTUAL_INTENTS
        and bool(settings.agent_require_citations)
        and final_citations
        and not valid_current
    ):
        warnings.append("Citations were auto-attached from retrieved evidence to keep the answer source-backed.")

    return {
        "citations": final_citations,
        "warnings": _dedupe_strings(warnings),
    }


def route_intent(state: TaxAuditAgentState) -> str:
    intent = state.get("intent") or INTENT_UNSUPPORTED
    return {
        INTENT_RISK_SUMMARY: "risk_summary",
        INTENT_RISK_LISTING: "risk_listing",
        INTENT_RISK_EXPLANATION: "risk_explanation",
        INTENT_EVIDENCE_SEARCH: "evidence_search",
        INTENT_SOURCE_TRACE: "source_trace",
        INTENT_UNSUPPORTED: "unsupported",
    }.get(intent, "unsupported")


def _ensure_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _dedupe_strings(values: list[str]) -> list[str]:
    return [value for value in dict.fromkeys(value.strip() for value in values if value and value.strip())]


def _dedupe_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        citation = item.get("citation") if isinstance(item.get("citation"), dict) else {}
        source_type = str(citation.get("source_type") or item.get("source_type") or "")
        source_id = str(citation.get("source_id") or item.get("source_id") or "")
        chunk_id = str(citation.get("chunk_id") or "")
        key = (source_type, source_id, chunk_id)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _extract_source_traces(
    evidence: list[dict[str, Any]],
    *,
    include_source_trace: bool,
) -> list[dict[str, Any]]:
    if not include_source_trace:
        return []

    traces: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        trace = item.get("source_trace")
        if not isinstance(trace, dict):
            continue

        source_type = str(trace.get("source_type") or item.get("source_type") or "")
        source_id = str(trace.get("source_id") or trace.get("risk_finding_id") or item.get("source_id") or "")
        if not source_type:
            source_type = KNOWLEDGE_SOURCE_TYPE_RISK_FINDING

        key = (source_type, source_id)
        if key in seen:
            continue
        seen.add(key)

        trace_payload = dict(trace)
        trace_payload.setdefault("source_type", source_type)
        if source_id:
            trace_payload.setdefault("source_id", source_id)
        traces.append(trace_payload)

    return traces


def _extract_source_reference(text: str) -> tuple[str | None, str | None]:
    pattern = re.compile(
        r"(?P<source_type>risk_finding|normalized_record|extracted_record)\s*[:#-]?\s*(?P<source_id>[0-9a-fA-F-]{8,})"
    )
    match = pattern.search(text or "")
    if not match:
        return None, None

    return (
        (match.group("source_type") or "").strip().lower() or None,
        (match.group("source_id") or "").strip() or None,
    )
