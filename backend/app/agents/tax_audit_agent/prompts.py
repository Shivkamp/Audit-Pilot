from __future__ import annotations

import json
from typing import Any

from app.agents.tax_audit_agent.intents import INTENT_RISK_LISTING
from app.agents.tax_audit_agent.state import TaxAuditAgentState
from app.core.config import settings
from app.llm.base import LLMMessage

GROUNDED_SYSTEM_PROMPT = """
You are TaxAudit AI.

Answer only from the provided risk findings, evidence, and source traces.
Do not invent risks, vendors, invoices, amounts, tax sections, challans, or citations.
Do not create new risk findings.
Do not perform fresh tax calculations unless values are explicitly provided.
If evidence is insufficient, explicitly say data is insufficient.
Mention that findings are based on processed workspace data.
Keep the answer concise but useful.
Do NOT include raw UUIDs, database IDs, workspace IDs, or any internal record identifiers ANYWHERE in your response — not in headings, titles, summaries, or body text.
Never reference a workspace by its ID. If you must refer to the workspace, say "this workspace" or use the workspace name if available.
Citations are surfaced separately; do not repeat them inline.

IMPORTANT — answering "missing data" questions:
When a user asks about missing values (e.g. "missing PAN", "missing TAN", "missing document"),
the answer must list WHICH vendors, invoices, or records have that issue — not the absent values
themselves (which do not exist in the data by definition).
For example, "show me all missing PANs" means: list vendors where PAN is absent, using the
vendor_code, vendor_name, and severity fields from risk_data or risk findings.
Always produce a clear list or table from the available risk_findings data.
Never return an empty response; if you have risk findings, summarise them.
""".strip()


def build_grounded_answer_messages(state: TaxAuditAgentState) -> list[LLMMessage]:
    max_evidence = int(state.get("max_evidence") or 6)
    intent = state.get("intent", "")

    safe_user_message = _sanitize_tag_content(state.get("user_message", ""))

    # For listing intents pass a compact row-per-line representation instead of
    # the full bulky JSON.  This keeps the prompt small enough that the LLM
    # reliably produces a response even when there are 50-200 findings.
    risk_findings_raw = state.get("risk_findings") or []
    if intent == INTENT_RISK_LISTING:
        findings_block = _compact_findings_for_listing(risk_findings_raw)
        findings_section = f"<RISK_FINDINGS_TABLE>\n{findings_block}\n</RISK_FINDINGS_TABLE>"
    else:
        findings_limit = int(settings.agent_retrieval_max_limit)
        risk_findings_trimmed = _trim_items(
            risk_findings_raw[:findings_limit],
            text_keys=("description", "title"),
            dict_keys=("risk_data",),
        )
        findings_section = f"<RISK_FINDINGS_JSON>{_as_json(risk_findings_trimmed)}</RISK_FINDINGS_JSON>"

    evidence_trimmed = _trim_items(
        (state.get("evidence") or [])[:max_evidence],
        text_keys=("content",),
        dict_keys=("facts",),
    )
    source_traces_trimmed = _trim_items(
        (state.get("source_traces") or [])[:max_evidence],
        dict_keys=("raw_data", "records", "metadata"),
    )

    user_prompt = "\n".join(
        [
            "Use the context below to answer the user.",
            f"<USER_MESSAGE>{safe_user_message}</USER_MESSAGE>",
            f"<INTENT>{intent}</INTENT>",
            f"<RISK_SUMMARY_JSON>{_as_json(state.get('risk_summary'))}</RISK_SUMMARY_JSON>",
            findings_section,
            f"<EVIDENCE_JSON>{_as_json(evidence_trimmed)}</EVIDENCE_JSON>",
            f"<SOURCE_TRACES_JSON>{_as_json(source_traces_trimmed)}</SOURCE_TRACES_JSON>",
        ]
    )

    return [
        LLMMessage(role="system", content=GROUNDED_SYSTEM_PROMPT),
        LLMMessage(role="user", content=user_prompt),
    ]


def _as_json(payload: Any) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, default=str)
    except TypeError:
        return json.dumps({}, ensure_ascii=False)


_MAX_TEXT_FIELD_LEN = 500
_MAX_DICT_FIELD_LEN = 1000


def _compact_findings_for_listing(findings: list[dict[str, Any]]) -> str:
    """Produce a compact pipe-separated table row for each finding.

    Keeps the prompt small for listing intents so the LLM can reliably
    produce a response even when there are 100+ findings.
    """
    if not findings:
        return "(no findings)"
    lines = ["Vendor Code | Vendor Name | Risk Type | Severity"]
    for f in findings:
        if not isinstance(f, dict):
            continue
        risk_data = f.get("risk_data") or {}
        vendor_code = risk_data.get("vendor_code") or f.get("vendor_code") or "-"
        vendor_name = risk_data.get("vendor_name") or f.get("vendor_name") or "-"
        risk_type = (f.get("risk_type") or "-").replace("_", " ").title()
        severity = (f.get("severity") or "-").upper()
        lines.append(f"{vendor_code} | {vendor_name} | {risk_type} | {severity}")
    return "\n".join(lines)


def _sanitize_tag_content(text: str) -> str:
    return (text or "").replace("<", "&lt;").replace(">", "&gt;")


def _trim_items(
    items: list[dict[str, Any]],
    *,
    text_keys: tuple[str, ...] = (),
    dict_keys: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    trimmed: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        copy = dict(item)
        for key in text_keys:
            val = copy.get(key)
            if isinstance(val, str) and len(val) > _MAX_TEXT_FIELD_LEN:
                copy[key] = val[:_MAX_TEXT_FIELD_LEN] + "..."
        for key in dict_keys:
            val = copy.get(key)
            if val is not None:
                serialized = json.dumps(val, ensure_ascii=False, default=str)
                if len(serialized) > _MAX_DICT_FIELD_LEN:
                    copy[key] = {"_truncated": True}
        trimmed.append(copy)
    return trimmed
