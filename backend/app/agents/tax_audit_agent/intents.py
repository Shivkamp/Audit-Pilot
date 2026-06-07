from __future__ import annotations

from collections.abc import Iterable

from app.core.config import settings
from app.llm.base import LLMMessage
from app.llm.service import LLMService

INTENT_RISK_SUMMARY = "risk_summary"
INTENT_RISK_LISTING = "risk_listing"
INTENT_RISK_EXPLANATION = "risk_explanation"
INTENT_EVIDENCE_SEARCH = "evidence_search"
INTENT_SOURCE_TRACE = "source_trace"
INTENT_UNSUPPORTED = "unsupported"

SUPPORTED_INTENTS = {
    INTENT_RISK_SUMMARY,
    INTENT_RISK_LISTING,
    INTENT_RISK_EXPLANATION,
    INTENT_EVIDENCE_SEARCH,
    INTENT_SOURCE_TRACE,
    INTENT_UNSUPPORTED,
}


def classify_intent(message: str, llm_service: LLMService | None = None) -> tuple[str, float]:
    deterministic_intent, deterministic_confidence = classify_intent_deterministic(message)

    if deterministic_intent not in {INTENT_EVIDENCE_SEARCH, INTENT_UNSUPPORTED}:
        return deterministic_intent, deterministic_confidence

    if not settings.agent_enable_llm_intent_fallback or llm_service is None:
        return deterministic_intent, deterministic_confidence

    llm_intent = _classify_intent_with_llm(message, llm_service)
    if llm_intent is None:
        return deterministic_intent, deterministic_confidence

    return llm_intent, 0.65


def classify_intent_deterministic(message: str) -> tuple[str, float]:
    text = (message or "").strip().lower()
    if not text:
        return INTENT_UNSUPPORTED, 0.0

    if _contains_any(
        text,
        {
            "where did this come from",
            "where did this risk come from",
            "where does this come from",
            "source trace",
            "source of",
            "trace back",
            "trace this",
            "trace the",
            "origin of",
            "came from",
        },
    ):
        return INTENT_SOURCE_TRACE, 0.96

    if _contains_any(
        text,
        {
            "what are the risks",
            "what are risks",
            "what risks",
            "risks in my data",
            "risks with my data",
            "risks in this data",
            "risks in the data",
            "summarize risks",
            "summarise risks",
            "risk summary",
            "audit red flags",
            "summarize my risk findings",
            "show me risks",
            "any risks",
            "overview of risks",
        },
    ):
        return INTENT_RISK_SUMMARY, 0.94

    if _contains_any(
        text,
        {
            # explicit listing verbs
            "list",
            "show all",
            "tell me all",
            "give me all",
            "get all",
            "fetch all",
            "display all",
            "show me all",
            # listing by entity
            "which vendors",
            "which invoices",
            "which records",
            "which rows",
            # risk-specific listing
            "all risks",
            "all risk",
            "all findings",
            "all the findings",
            "all the risks",
            "list risks",
            "list risk findings",
            # "missing X" domain patterns — user is asking to enumerate records with absent data
            "missing pan",
            "missing tan",
            "missing gstin",
            "missing document",
            "missing invoice",
            "missing supporting",
            "pan missing",
            "tan missing",
            # generic "all the <noun>" pattern
            "all the missing",
            "all missing",
            # show/tell/give me all rows / records
            "all rows",
            "all records",
        },
    ):
        return INTENT_RISK_LISTING, 0.9

    if _contains_any(
        text,
        {
            "why",
            "explain",
            "reason",
            "flagged",
            "how is this a risk",
            "why was",
        },
    ):
        return INTENT_RISK_EXPLANATION, 0.9

    if _contains_any(
        text,
        {
            "evidence",
            "show evidence",
            "supporting",
            "proof",
            "find records",
            "search",
        },
    ):
        return INTENT_EVIDENCE_SEARCH, 0.78

    if "risk" in text:
        return INTENT_EVIDENCE_SEARCH, 0.62

    return INTENT_UNSUPPORTED, 0.45


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def _classify_intent_with_llm(message: str, llm_service: LLMService) -> str | None:
    prompt = (
        "Classify the user message into exactly one intent token.\n"
        f"Allowed intents: {', '.join(sorted(SUPPORTED_INTENTS))}.\n"
        "Return only the intent token and nothing else."
    )

    try:
        response = llm_service.generate(
            messages=[
                LLMMessage(role="system", content=prompt),
                LLMMessage(role="user", content=message or ""),
            ],
            temperature=0.0,
            max_tokens=16,
        )
    except Exception:
        return None

    token = (response.content or "").strip().lower().split()[0] if response.content else ""
    if token in SUPPORTED_INTENTS:
        return token

    return None
