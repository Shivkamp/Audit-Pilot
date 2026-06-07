from __future__ import annotations

from typing import Sequence, cast

from app.core.config import settings
from app.core.constants import AGENT_CHAT_UNSUPPORTED_LLM_PROVIDER
from app.core.exceptions import AppException
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.llm.providers import CerebrasLLMProvider, MockLLMProvider


class LLMService:
    def __init__(self, provider_name: str | None = None) -> None:
        selected = provider_name if provider_name is not None else settings.llm_provider
        self._provider_name = (selected or "mock").strip().lower()
        self._provider: BaseLLMProvider | None = None

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def generate(
        self,
        messages: Sequence[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        provider = self._resolve_provider()
        return provider.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._provider is not None:
            return self._provider

        if self._provider_name == "mock":
            self._provider = cast(BaseLLMProvider, MockLLMProvider())
            return self._provider

        if self._provider_name == "cerebras":
            self._provider = cast(BaseLLMProvider, CerebrasLLMProvider())
            return self._provider

        raise AppException(
            message=f"Unsupported LLM provider: {self._provider_name}.",
            error_code=AGENT_CHAT_UNSUPPORTED_LLM_PROVIDER,
        )
