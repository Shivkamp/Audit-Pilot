from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class NormalizedItem:
    source_record_id: UUID | None
    record_category: str
    normalized_data: dict[str, Any]
    normalization_status: str
    normalization_confidence: float | None = None
    normalization_errors: list[dict[str, Any]] | None = None


class BaseNormalizer(ABC):
    @abstractmethod
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        raise NotImplementedError

    def normalize_batch(self, extracted_records: list[Any]) -> list[NormalizedItem]:
        return [self.normalize_record(record) for record in extracted_records]