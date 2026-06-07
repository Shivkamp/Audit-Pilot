from __future__ import annotations

import hashlib
import math
import re

from app.embeddings.base import EmbeddingProvider

_TOKEN_PATTERN = re.compile(r"\w+")


class LocalHashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int) -> None:
        self.dimension = max(1, int(dimension))

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        tokens = self._tokenize(text)
        if not tokens:
            return self._zero_vector()

        vector = [0.0 for _ in range(self.dimension)]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], byteorder="big", signed=False) % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        return self._normalize(vector)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]

    def _tokenize(self, text: str) -> list[str]:
        return [token.lower() for token in _TOKEN_PATTERN.findall(text)]

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return self._zero_vector()

        return [value / norm for value in vector]

    def _zero_vector(self) -> list[float]:
        return [0.0 for _ in range(self.dimension)]
