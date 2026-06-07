from __future__ import annotations

from fastapi import status

from app.core.config import settings
from app.core.constants import (
    EMBEDDING_PROVIDER_LOCAL_HASH,
    KNOWLEDGE_UNSUPPORTED_EMBEDDING_PROVIDER,
)
from app.core.exceptions import AppException
from app.embeddings.base import EmbeddingProvider
from app.embeddings.local_hash_provider import LocalHashEmbeddingProvider


class EmbeddingService:
    def __init__(
        self,
        *,
        provider_name: str | None = None,
        model_name: str | None = None,
        dimension: int | None = None,
    ) -> None:
        self.provider_name = provider_name or settings.embedding_provider
        self.model_name = model_name or settings.embedding_model
        self.dimension = max(1, int(dimension or settings.embedding_dimension))
        self._provider = self._build_provider()

    def embed_text(self, text: str) -> list[float]:
        return self._provider.embed_text(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self._provider.embed_batch(texts)

    def _build_provider(self) -> EmbeddingProvider:
        if self.provider_name == EMBEDDING_PROVIDER_LOCAL_HASH:
            return LocalHashEmbeddingProvider(dimension=self.dimension)

        raise AppException(
            message="Unsupported embedding provider configured.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=KNOWLEDGE_UNSUPPORTED_EMBEDDING_PROVIDER,
        )
