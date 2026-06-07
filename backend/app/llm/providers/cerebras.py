from __future__ import annotations

from typing import Any, Sequence

from openai import OpenAI, RateLimitError

from app.core.config import settings
from app.core.constants import (
    AGENT_CHAT_CEREBRAS_API_KEY_REQUIRED,
    AGENT_CHAT_LLM_PROVIDER_ERROR,
    AGENT_CHAT_LLM_RATE_LIMITED,
)
from app.core.exceptions import AppException
from app.core.logging import logger
from app.llm.base import LLMMessage, LLMResponse


class CerebrasLLMProvider:
    provider_name = "cerebras"

    def __init__(self) -> None:
        self.model_name = settings.cerebras_model
        api_key = (settings.cerebras_api_key or "").strip()
        if not api_key:
            raise AppException(
                message="Cerebras API key is required when LLM_PROVIDER=cerebras.",
                error_code=AGENT_CHAT_CEREBRAS_API_KEY_REQUIRED,
            )

        self._client = OpenAI(
            api_key=api_key,
            base_url=settings.cerebras_base_url,
            timeout=float(settings.llm_timeout_seconds),
            max_retries=int(settings.llm_max_retries),
        )

    def generate(
        self,
        messages: Sequence[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages
                ],
                temperature=(
                    float(temperature)
                    if temperature is not None
                    else float(settings.llm_temperature)
                ),
                max_tokens=(
                    int(max_tokens)
                    if max_tokens is not None
                    else int(settings.llm_max_tokens)
                ),
            )

            content = ""
            if response.choices:
                content = response.choices[0].message.content or ""

            usage: dict[str, Any] | None = None
            if response.usage is not None:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return LLMResponse(
                content=content.strip(),
                model=response.model or self.model_name,
                provider=self.provider_name,
                usage=usage,
                raw=response.model_dump(),
            )
        except AppException:
            raise
        except RateLimitError as exc:
            logger.warning("Cerebras rate limited: %s", exc)
            raise AppException(
                message="The LLM provider is experiencing high traffic. Please try again in a moment.",
                status_code=429,
                error_code=AGENT_CHAT_LLM_RATE_LIMITED,
            ) from exc
        except Exception as exc:
            logger.error("Cerebras LLM generation failed: %s", exc)
            raise AppException(
                message="Cerebras generation failed.",
                status_code=502,
                error_code=AGENT_CHAT_LLM_PROVIDER_ERROR,
            ) from exc
