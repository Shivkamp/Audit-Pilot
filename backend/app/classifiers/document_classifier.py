from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.core.constants import (
    DOCUMENT_TYPE_FORM_26AS,
    DOCUMENT_TYPE_INVOICE,
    DOCUMENT_TYPE_TDS_CHALLAN,
    DOCUMENT_TYPE_TDS_WORKING,
    DOCUMENT_TYPE_UNKNOWN,
    DOCUMENT_TYPE_VENDOR_LEDGER,
    DOCUMENT_TYPE_VENDOR_MASTER,
)


@dataclass(frozen=True)
class ClassificationEvidence:
    original_filename: str
    file_extension: str | None = None
    content_type: str | None = None
    sheet_names: list[str] = field(default_factory=list)
    column_names: list[str] = field(default_factory=list)
    sample_text: str = ""
    sample_raw_data: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ClassificationResult:
    document_type: str
    confidence: float
    method: str
    reason: dict[str, Any]


class DocumentClassifier:
    METHOD = "rule_based_v1"

    _CLASSIFIABLE_TYPES = (
        DOCUMENT_TYPE_VENDOR_LEDGER,
        DOCUMENT_TYPE_TDS_WORKING,
        DOCUMENT_TYPE_VENDOR_MASTER,
        DOCUMENT_TYPE_INVOICE,
        DOCUMENT_TYPE_TDS_CHALLAN,
        DOCUMENT_TYPE_FORM_26AS,
    )

    _FILENAME_SIGNALS: dict[str, tuple[str, ...]] = {
        DOCUMENT_TYPE_VENDOR_MASTER: ("vendor_master", "vendor master"),
        DOCUMENT_TYPE_VENDOR_LEDGER: ("vendor_ledger", "vendor ledger", "ledger"),
        DOCUMENT_TYPE_TDS_WORKING: ("tds_working", "tds working"),
        DOCUMENT_TYPE_TDS_CHALLAN: ("challan",),
        DOCUMENT_TYPE_FORM_26AS: ("26as", "form 26as"),
        DOCUMENT_TYPE_INVOICE: ("invoice",),
    }

    _SHEET_SIGNALS: dict[str, tuple[str, ...]] = {
        DOCUMENT_TYPE_VENDOR_MASTER: ("vendor_master", "vendor master"),
        DOCUMENT_TYPE_VENDOR_LEDGER: ("vendor_ledger", "vendor ledger", "ledger"),
        DOCUMENT_TYPE_TDS_WORKING: ("tds_working", "tds working"),
        DOCUMENT_TYPE_TDS_CHALLAN: ("challan",),
        DOCUMENT_TYPE_FORM_26AS: ("26as", "form 26as"),
    }

    _COLUMN_SIGNALS: dict[str, tuple[str, ...]] = {
        DOCUMENT_TYPE_VENDOR_MASTER: (
            "vendor_code",
            "vendor_name",
            "pan",
            "gstin",
            "vendor_type",
            "status",
        ),
        DOCUMENT_TYPE_VENDOR_LEDGER: (
            "transaction_date",
            "posting_date",
            "invoice_no",
            "invoice_number",
            "gross_amount",
            "vendor_name",
            "ledger_tds_section",
            "tds_deducted_as_per_ledger",
            "payment_status",
            "expense_head",
            "narration",
        ),
        DOCUMENT_TYPE_TDS_WORKING: (
            "deduction_month",
            "tds_section",
            "tds_rate",
            "amount_paid_or_credited",
            "tds_required_as_per_working",
            "tds_deducted_as_per_working",
            "tds_required",
            "tds_deducted",
            "tds_difference",
            "vendor_pan",
        ),
        DOCUMENT_TYPE_TDS_CHALLAN: (
            "challan_serial_no",
            "bsr_code",
            "tds_deposited_as_per_challan",
            "deposit_date",
            "tan",
        ),
        DOCUMENT_TYPE_FORM_26AS: (
            "assessee_pan",
            "deductor_tan",
            "deductor_name",
            "tax_deposited",
            "challan_serial_no",
            "statement_row_id",
            "amount_reported_in_26as",
            "match_status_hint",
        ),
        DOCUMENT_TYPE_INVOICE: (
            "invoice_no",
            "invoice_date",
            "supplier",
            "customer",
            "gross_amount",
        ),
    }

    _TEXT_SIGNALS: dict[str, tuple[str, ...]] = {
        DOCUMENT_TYPE_INVOICE: (
            "tax invoice",
            "invoice no",
            "invoice date",
            "supplier",
            "customer",
            "gross amount",
        ),
        DOCUMENT_TYPE_TDS_CHALLAN: (
            "tds challan",
            "challan",
            "bsr code",
            "tan",
            "tds deposited",
        ),
        DOCUMENT_TYPE_FORM_26AS: (
            "form 26as",
            "annual tax statement",
            "assessee",
            "deductor",
            "tax deposited",
        ),
    }

    _COLUMN_GROUP_BONUS_THRESHOLD: dict[str, int] = {
        DOCUMENT_TYPE_TDS_WORKING: 4,
        DOCUMENT_TYPE_VENDOR_LEDGER: 4,
        DOCUMENT_TYPE_VENDOR_MASTER: 4,
        DOCUMENT_TYPE_TDS_CHALLAN: 3,
        DOCUMENT_TYPE_FORM_26AS: 3,
    }

    def __init__(self, *, min_confidence: float, ambiguity_margin: int) -> None:
        self._min_confidence = min_confidence
        self._ambiguity_margin = ambiguity_margin

    def classify(self, evidence: ClassificationEvidence) -> ClassificationResult:
        scores = {document_type: 0 for document_type in self._CLASSIFIABLE_TYPES}
        matched_signals: list[dict[str, Any]] = []

        self._apply_filename_signals(scores, matched_signals, evidence.original_filename)
        self._apply_sheet_signals(scores, matched_signals, evidence.sheet_names)
        self._apply_extension_signals(
            scores,
            matched_signals,
            evidence.file_extension,
            evidence.content_type,
        )

        normalized_columns = self._collect_normalized_columns(evidence)
        self._apply_column_signals(scores, matched_signals, normalized_columns)
        self._apply_text_signals(scores, matched_signals, evidence.sample_text)

        ranked_scores = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        winning_type, winning_score = ranked_scores[0]
        second_best_type, second_best_score = ranked_scores[1]

        confidence = 0.0
        if winning_score > 0:
            confidence = round(min(0.99, winning_score / 25), 4)

        final_document_type = winning_type
        unknown_reason: str | None = None

        if winning_score <= 0:
            final_document_type = DOCUMENT_TYPE_UNKNOWN
            unknown_reason = "no_positive_signals"
        elif confidence < self._min_confidence:
            final_document_type = DOCUMENT_TYPE_UNKNOWN
            unknown_reason = "below_min_confidence"
        elif (winning_score - second_best_score) < self._ambiguity_margin:
            final_document_type = DOCUMENT_TYPE_UNKNOWN
            unknown_reason = "ambiguous_scores"

        reason: dict[str, Any] = {
            "matched_signals": matched_signals,
            "scores": scores,
            "winning_type": winning_type,
            "winning_score": winning_score,
            "second_best_type": second_best_type,
            "second_best_score": second_best_score,
            "score_gap": winning_score - second_best_score,
            "min_confidence": self._min_confidence,
            "ambiguity_margin": self._ambiguity_margin,
        }
        if unknown_reason is not None:
            reason["unknown_reason"] = unknown_reason

        return ClassificationResult(
            document_type=final_document_type,
            confidence=confidence,
            method=self.METHOD,
            reason=reason,
        )

    def _apply_filename_signals(
        self,
        scores: dict[str, int],
        matched_signals: list[dict[str, Any]],
        original_filename: str,
    ) -> None:
        raw_filename = (original_filename or "").lower()
        normalized_filename = self._normalize_text_for_lookup(original_filename)

        for document_type, candidates in self._FILENAME_SIGNALS.items():
            matched_candidate = next(
                (
                    candidate
                    for candidate in candidates
                    if self._contains_signal(raw_filename, normalized_filename, candidate)
                ),
                None,
            )
            if matched_candidate:
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=5,
                    signal_type="filename",
                    signal_value=matched_candidate,
                )

    def _apply_sheet_signals(
        self,
        scores: dict[str, int],
        matched_signals: list[dict[str, Any]],
        sheet_names: list[str],
    ) -> None:
        for document_type, candidates in self._SHEET_SIGNALS.items():
            found_match = False
            for sheet_name in sheet_names:
                raw_sheet_name = (sheet_name or "").lower()
                normalized_sheet_name = self._normalize_text_for_lookup(sheet_name)
                matched_candidate = next(
                    (
                        candidate
                        for candidate in candidates
                        if self._contains_signal(
                            raw_sheet_name,
                            normalized_sheet_name,
                            candidate,
                        )
                    ),
                    None,
                )
                if matched_candidate is None:
                    continue

                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=5,
                    signal_type="sheet_name",
                    signal_value=f"{sheet_name}:{matched_candidate}",
                )
                found_match = True
                break

            if found_match:
                continue

    def _apply_extension_signals(
        self,
        scores: dict[str, int],
        matched_signals: list[dict[str, Any]],
        file_extension: str | None,
        content_type: str | None,
    ) -> None:
        normalized_extension = (file_extension or "").lower().strip()
        normalized_content_type = (content_type or "").lower().strip()

        if normalized_extension == ".pdf":
            for document_type in (
                DOCUMENT_TYPE_INVOICE,
                DOCUMENT_TYPE_TDS_CHALLAN,
                DOCUMENT_TYPE_FORM_26AS,
            ):
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=1,
                    signal_type="file_extension",
                    signal_value=normalized_extension,
                )
        elif normalized_extension in {".xlsx", ".xls", ".csv"}:
            for document_type in (
                DOCUMENT_TYPE_VENDOR_MASTER,
                DOCUMENT_TYPE_VENDOR_LEDGER,
                DOCUMENT_TYPE_TDS_WORKING,
                DOCUMENT_TYPE_TDS_CHALLAN,
                DOCUMENT_TYPE_FORM_26AS,
            ):
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=1,
                    signal_type="file_extension",
                    signal_value=normalized_extension,
                )

        if "pdf" in normalized_content_type:
            for document_type in (
                DOCUMENT_TYPE_INVOICE,
                DOCUMENT_TYPE_TDS_CHALLAN,
                DOCUMENT_TYPE_FORM_26AS,
            ):
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=1,
                    signal_type="content_type",
                    signal_value=normalized_content_type,
                )

        if any(
            token in normalized_content_type
            for token in ("sheet", "excel", "spreadsheet", "csv")
        ):
            for document_type in (
                DOCUMENT_TYPE_VENDOR_MASTER,
                DOCUMENT_TYPE_VENDOR_LEDGER,
                DOCUMENT_TYPE_TDS_WORKING,
                DOCUMENT_TYPE_TDS_CHALLAN,
                DOCUMENT_TYPE_FORM_26AS,
            ):
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=1,
                    signal_type="content_type",
                    signal_value=normalized_content_type,
                )

    def _collect_normalized_columns(self, evidence: ClassificationEvidence) -> set[str]:
        columns: set[str] = set()

        for column in evidence.column_names:
            normalized_column = self._normalize_field_name(column)
            if normalized_column:
                columns.add(normalized_column)

        for raw_row in evidence.sample_raw_data:
            if not isinstance(raw_row, dict):
                continue
            for key in raw_row.keys():
                normalized_key = self._normalize_field_name(str(key))
                if normalized_key:
                    columns.add(normalized_key)

        return columns

    def _apply_column_signals(
        self,
        scores: dict[str, int],
        matched_signals: list[dict[str, Any]],
        normalized_columns: set[str],
    ) -> None:
        for document_type, expected_columns in self._COLUMN_SIGNALS.items():
            matched_columns = [
                column_name
                for column_name in expected_columns
                if self._normalize_field_name(column_name) in normalized_columns
            ]

            for matched_column in matched_columns:
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=2,
                    signal_type="column",
                    signal_value=matched_column,
                )

            threshold = self._COLUMN_GROUP_BONUS_THRESHOLD.get(document_type)
            if threshold is not None and len(matched_columns) >= threshold:
                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=8,
                    signal_type="column_group_bonus",
                    signal_value=f"{len(matched_columns)}_columns",
                )

    def _apply_text_signals(
        self,
        scores: dict[str, int],
        matched_signals: list[dict[str, Any]],
        sample_text: str,
    ) -> None:
        raw_text = (sample_text or "").lower()
        normalized_text = self._normalize_text_for_lookup(sample_text)

        for document_type, text_candidates in self._TEXT_SIGNALS.items():
            for text_candidate in text_candidates:
                if not self._contains_signal(raw_text, normalized_text, text_candidate):
                    continue

                self._add_score(
                    scores,
                    matched_signals,
                    document_type=document_type,
                    points=2,
                    signal_type="text",
                    signal_value=text_candidate,
                )

        if self._contains_signal(raw_text, normalized_text, "tax invoice") and self._contains_signal(
            raw_text,
            normalized_text,
            "invoice no",
        ):
            self._add_score(
                scores,
                matched_signals,
                document_type=DOCUMENT_TYPE_INVOICE,
                points=8,
                signal_type="text_group_bonus",
                signal_value="tax_invoice+invoice_no",
            )

        if self._contains_signal(raw_text, normalized_text, "form 26as") and self._contains_signal(
            raw_text,
            normalized_text,
            "deductor",
        ):
            self._add_score(
                scores,
                matched_signals,
                document_type=DOCUMENT_TYPE_FORM_26AS,
                points=8,
                signal_type="text_group_bonus",
                signal_value="form_26as+deductor",
            )

        if self._contains_signal(raw_text, normalized_text, "challan") and self._contains_signal(
            raw_text,
            normalized_text,
            "bsr code",
        ):
            self._add_score(
                scores,
                matched_signals,
                document_type=DOCUMENT_TYPE_TDS_CHALLAN,
                points=8,
                signal_type="text_group_bonus",
                signal_value="challan+bsr_code",
            )

    @classmethod
    def _contains_signal(
        cls,
        raw_text: str,
        normalized_text: str,
        signal: str,
    ) -> bool:
        lower_signal = signal.lower()
        normalized_signal = cls._normalize_text_for_lookup(signal)
        return lower_signal in raw_text or normalized_signal in normalized_text

    @staticmethod
    def _add_score(
        scores: dict[str, int],
        matched_signals: list[dict[str, Any]],
        *,
        document_type: str,
        points: int,
        signal_type: str,
        signal_value: str,
    ) -> None:
        scores[document_type] += points
        matched_signals.append(
            {
                "document_type": document_type,
                "signal_type": signal_type,
                "signal": signal_value,
                "points": points,
            }
        )

    @staticmethod
    def _normalize_text_for_lookup(value: str | None) -> str:
        normalized = (value or "").strip().lower()
        normalized = normalized.replace("-", " ").replace("_", " ")
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    @staticmethod
    def _normalize_field_name(value: str | None) -> str:
        normalized = (value or "").strip().lower()
        normalized = re.sub(r"[\s\-]+", "_", normalized)
        normalized = re.sub(r"[^a-z0-9_]", "", normalized)
        normalized = re.sub(r"_+", "_", normalized)
        return normalized.strip("_")
