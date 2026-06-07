from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, Any] | None = None
    raw: Any | None = None


class BaseLLMProvider(Protocol):
    provider_name: str
    model_name: str

    def generate(
        self,
        messages: Sequence[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        ...
