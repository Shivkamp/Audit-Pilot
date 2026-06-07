from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Sequence

from app.llm.base import LLMMessage, LLMResponse


class MockLLMProvider:
    provider_name = "mock"
    model_name = "mock-grounded-v1"

    def generate(
        self,
        messages: Sequence[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        _ = (temperature, max_tokens)
        prompt = "\n\n".join(f"{message.role}: {message.content}" for message in messages)
        payload = self._extract_payload(prompt)
        answer = self._build_answer(payload)

        return LLMResponse(
            content=answer,
            model=self.model_name,
            provider=self.provider_name,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            raw={"mock": True},
        )

    def _extract_payload(self, prompt: str) -> dict[str, Any]:
        return {
            "user_message": self._extract_text_block(prompt, "USER_MESSAGE") or "",
            "intent": self._extract_text_block(prompt, "INTENT") or "",
            "risk_summary": self._extract_json_block(prompt, "RISK_SUMMARY_JSON", default=None),
            "risk_findings": self._extract_json_block(prompt, "RISK_FINDINGS_JSON", default=[]),
            "evidence": self._extract_json_block(prompt, "EVIDENCE_JSON", default=[]),
            "source_traces": self._extract_json_block(prompt, "SOURCE_TRACES_JSON", default=[]),
        }

    def _extract_text_block(self, text: str, tag: str) -> str | None:
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        return match.group(1).strip()

    def _extract_json_block(self, text: str, tag: str, default: Any) -> Any:
        raw = self._extract_text_block(text, tag)
        if not raw:
            return default
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default

    def _build_answer(self, payload: dict[str, Any]) -> str:
        user_message = str(payload.get("user_message") or "").strip()
        intent = str(payload.get("intent") or "").strip() or "evidence_search"
        risk_summary = payload.get("risk_summary") if isinstance(payload.get("risk_summary"), dict) else {}
        risk_findings = payload.get("risk_findings") if isinstance(payload.get("risk_findings"), list) else []
        evidence = payload.get("evidence") if isinstance(payload.get("evidence"), list) else []
        source_traces = payload.get("source_traces") if isinstance(payload.get("source_traces"), list) else []

        if not risk_findings and not evidence and not source_traces:
            return (
                "I don’t have enough processed workspace evidence to answer this confidently yet. "
                "Please run risk checks and knowledge retrieval first, then try again."
            )

        lines: list[str] = [
            "Based on processed workspace data, here is a grounded summary.",
        ]

        total_findings = int(risk_summary.get("total_findings") or 0)
        if total_findings > 0:
            lines.append(f"- Total risk findings: {total_findings}.")

        if risk_findings:
            lines.append("- Key findings:")
            for finding in risk_findings[:3]:
                risk_type = str(finding.get("risk_type") or "risk").replace("_", " ")
                title = str(finding.get("title") or finding.get("description") or risk_type)
                severity = str(finding.get("severity") or "UNKNOWN")
                lines.append(f"  - {title} (type: {risk_type}, severity: {severity}).")

            risk_type_counts = Counter(
                str(finding.get("risk_type") or "unknown")
                for finding in risk_findings
                if isinstance(finding, dict)
            )
            if risk_type_counts:
                top_risk_type, top_count = sorted(
                    risk_type_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )[0]
                lines.append(
                    f"- Most frequent risk type in current findings: {top_risk_type.replace('_', ' ')} ({top_count})."
                )

        if evidence:
            refs: list[str] = []
            for item in evidence[:4]:
                if not isinstance(item, dict):
                    continue
                citation = item.get("citation") if isinstance(item.get("citation"), dict) else {}
                source_type = str(citation.get("source_type") or item.get("source_type") or "source")
                source_id = str(citation.get("source_id") or item.get("source_id") or "unknown")
                refs.append(f"{source_type}:{source_id}")
            if refs:
                lines.append(f"- Evidence references: {', '.join(dict.fromkeys(refs))}.")

        if source_traces:
            lines.append(f"- Source traces available: {len(source_traces)}.")

        if user_message:
            lines.append(f"Your question was interpreted as intent '{intent}'.")

        lines.append("These findings are based on processed workspace data only.")
        return "\n".join(lines)
