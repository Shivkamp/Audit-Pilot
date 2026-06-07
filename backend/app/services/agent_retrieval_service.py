from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    EMBEDDING_STATUS_EMBEDDED,
    KNOWLEDGE_INVALID_RISK_TYPE,
    KNOWLEDGE_SOURCE_NOT_FOUND,
    KNOWLEDGE_SOURCE_TYPE_EXTRACTED_RECORD,
    KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
    KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
    KNOWLEDGE_UNSUPPORTED_SOURCE_TYPE,
    RISK_FINDING_NOT_FOUND,
    RISK_TYPE_DUPLICATE_INVOICE,
    RISK_TYPE_HIGH_VALUE_TRANSACTION,
    RISK_TYPE_MISSING_PAN,
    RISK_TYPE_MISSING_SUPPORTING_DOCUMENT,
    RISK_TYPE_SHORT_DEPOSIT,
    RISK_TYPE_TDS_MISMATCH,
    RISK_TYPE_VENDOR_NAME_MISMATCH,
    RISK_TYPE_WRONG_TDS_SECTION,
)
from app.core.exceptions import AppException
from app.knowledge.source_trace import (
    build_citation,
    build_normalized_record_source_trace,
    build_risk_finding_source_trace,
)
from app.repositories.document_repository import DocumentRepository
from app.repositories.extraction_repository import ExtractionRepository
from app.repositories.knowledge_chunk_repository import KnowledgeChunkRepository
from app.repositories.normalization_repository import NormalizationRepository
from app.repositories.risk_finding_repository import RiskFindingRepository
from app.services.retrieval_service import RetrievalService
from app.services.workspace_service import WorkspaceService

_ALLOWED_RISK_TYPES = {
    RISK_TYPE_MISSING_PAN,
    RISK_TYPE_DUPLICATE_INVOICE,
    RISK_TYPE_TDS_MISMATCH,
    RISK_TYPE_SHORT_DEPOSIT,
    RISK_TYPE_VENDOR_NAME_MISMATCH,
    RISK_TYPE_WRONG_TDS_SECTION,
    RISK_TYPE_HIGH_VALUE_TRANSACTION,
    RISK_TYPE_MISSING_SUPPORTING_DOCUMENT,
}


class AgentRetrievalService:
    @staticmethod
    def retrieve_workspace_evidence(
        db: Session,
        workspace_id: UUID,
        query: str,
        limit: int,
        include_source_trace: bool = True,
    ) -> dict:
        safe_limit = max(1, min(limit, settings.agent_retrieval_max_limit))
        search_data = RetrievalService.search_workspace(db, workspace_id, query, safe_limit)

        evidence = AgentRetrievalService._build_evidence_items(
            db,
            workspace_id=workspace_id,
            results=search_data["results"],
            include_source_trace=include_source_trace,
        )

        return {
            "workspace_id": workspace_id,
            "query": search_data["query"],
            "limit": safe_limit,
            "evidence": evidence,
        }

    @staticmethod
    def retrieve_risk_evidence(
        db: Session,
        workspace_id: UUID,
        risk_type: str,
        query: str | None = None,
        limit: int = 5,
        include_source_trace: bool = True,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        clean_risk_type = (risk_type or "").strip()
        if clean_risk_type not in _ALLOWED_RISK_TYPES:
            raise AppException(
                message="Invalid risk type.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=KNOWLEDGE_INVALID_RISK_TYPE,
            )

        safe_limit = max(1, min(limit, settings.agent_retrieval_max_limit))

        filtered_results: list[dict] = []
        if query and query.strip():
            search_data = RetrievalService.search_workspace(
                db,
                workspace.id,
                query,
                max(safe_limit, settings.knowledge_search_default_limit),
                retrieval_options={"risk_type": clean_risk_type},
            )

            ranked_results = list(search_data["results"])
            filtered_results.extend(
                [
                    result
                    for result in ranked_results
                    if AgentRetrievalService._is_matching_risk_result(result, clean_risk_type)
                ]
            )

            existing_chunk_ids = {str(result["chunk_id"]) for result in filtered_results}
            for result in ranked_results:
                chunk_id = str(result.get("chunk_id"))
                if chunk_id in existing_chunk_ids:
                    continue

                if result.get("source_type") not in {
                    KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
                    KNOWLEDGE_SOURCE_TYPE_EXTRACTED_RECORD,
                }:
                    continue

                filtered_results.append(result)
                existing_chunk_ids.add(chunk_id)

                if len(filtered_results) >= safe_limit:
                    break

        if len(filtered_results) < safe_limit:
            fallback_chunks = KnowledgeChunkRepository.list_by_workspace(
                db,
                workspace.id,
                source_type=KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
                chunk_type=f"risk_{clean_risk_type}",
                embedding_status=EMBEDDING_STATUS_EMBEDDED,
                limit=safe_limit * 2,
                offset=0,
            )

            existing_chunk_ids = {str(result["chunk_id"]) for result in filtered_results}
            for chunk in fallback_chunks:
                chunk_id_str = str(chunk.id)
                if chunk_id_str in existing_chunk_ids:
                    continue

                filtered_results.append(
                    {
                        "chunk_id": chunk.id,
                        "score": 0.0,
                        "source_type": chunk.source_type,
                        "source_id": chunk.source_id,
                        "chunk_type": chunk.chunk_type,
                        "chunk_text": chunk.chunk_text,
                        "chunk_metadata": chunk.chunk_metadata or {},
                    }
                )
                existing_chunk_ids.add(chunk_id_str)

                if len(filtered_results) >= safe_limit:
                    break

        filtered_results = filtered_results[:safe_limit]

        evidence = AgentRetrievalService._build_evidence_items(
            db,
            workspace_id=workspace.id,
            results=filtered_results,
            include_source_trace=include_source_trace,
        )

        return {
            "workspace_id": workspace.id,
            "risk_type": clean_risk_type,
            "query": (query or "").strip() or None,
            "limit": safe_limit,
            "evidence": evidence,
        }

    @staticmethod
    def get_finding_context(db: Session, workspace_id: UUID, risk_finding_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        finding = RiskFindingRepository.get_by_id(db, risk_finding_id)
        if finding is None or finding.workspace_id != workspace.id:
            raise AppException(
                message="Risk finding not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=RISK_FINDING_NOT_FOUND,
            )

        normalized_records = AgentRetrievalService._get_related_normalized_records(
            db,
            workspace_id=workspace.id,
            finding=finding,
        )

        source_trace = AgentRetrievalService.get_source_trace(
            db,
            workspace_id=workspace.id,
            source_type=KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
            source_id=str(finding.id),
        )

        return {
            "workspace_id": workspace.id,
            "risk_finding": AgentRetrievalService._serialize_risk_finding(finding),
            "related_normalized_records": [
                AgentRetrievalService._serialize_normalized_record(record)
                for record in normalized_records
            ],
            "source_trace": source_trace,
        }

    @staticmethod
    def get_source_trace(
        db: Session,
        workspace_id: UUID,
        source_type: str,
        source_id: str,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        if source_type == KNOWLEDGE_SOURCE_TYPE_RISK_FINDING:
            finding = AgentRetrievalService._get_workspace_finding_by_source_id(
                db,
                workspace_id=workspace.id,
                source_id=source_id,
            )
            normalized_records = AgentRetrievalService._get_related_normalized_records(
                db,
                workspace_id=workspace.id,
                finding=finding,
            )
            extracted_records_by_id: dict[str, object] = {}
            for record in normalized_records:
                source_record_id = getattr(record, "source_record_id", None)
                if source_record_id is None:
                    continue

                extracted_record = ExtractionRepository.get_by_id(db, source_record_id)
                if extracted_record is None:
                    continue
                if extracted_record.workspace_id != workspace.id:
                    continue

                extracted_records_by_id[str(source_record_id)] = extracted_record

            trace = build_risk_finding_source_trace(
                source_id=str(finding.id),
                risk_finding=finding,
                normalized_records=normalized_records,
                extracted_records_by_id=extracted_records_by_id,
            )
            trace["documents"] = AgentRetrievalService._resolve_document_metadata(
                db,
                workspace_id=workspace.id,
                document_ids=trace.get("document_ids") or [],
            )
            return trace

        if source_type == KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD:
            normalized_record = AgentRetrievalService._get_workspace_normalized_record_by_source_id(
                db,
                workspace_id=workspace.id,
                source_id=source_id,
            )

            extracted_record = None
            source_record_id = getattr(normalized_record, "source_record_id", None)
            if source_record_id is not None:
                candidate_record = ExtractionRepository.get_by_id(db, source_record_id)
                if candidate_record is not None and candidate_record.workspace_id == workspace.id:
                    extracted_record = candidate_record

            trace = build_normalized_record_source_trace(
                source_id=str(normalized_record.id),
                normalized_record=normalized_record,
                extracted_record=extracted_record,
            )
            trace["documents"] = AgentRetrievalService._resolve_document_metadata(
                db,
                workspace_id=workspace.id,
                document_ids=trace.get("document_ids") or [],
            )
            return trace

        raise AppException(
            message="Unsupported source type for source trace.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=KNOWLEDGE_UNSUPPORTED_SOURCE_TYPE,
        )

    @staticmethod
    def _build_evidence_items(
        db: Session,
        *,
        workspace_id: UUID,
        results: list[dict],
        include_source_trace: bool,
    ) -> list[dict]:
        # Batch source-trace resolution: resolve each unique (source_type, source_id)
        # pair exactly once rather than once per evidence item.  Evidence from the same
        # risk finding or normalized record is very common when the pool has duplicates,
        # so this dedup alone eliminates the most expensive N-serial-DB-query pattern.
        _traceable_types = {
            KNOWLEDGE_SOURCE_TYPE_RISK_FINDING,
            KNOWLEDGE_SOURCE_TYPE_NORMALIZED_RECORD,
        }
        traces_cache: dict[tuple[str, str], dict | None] = {}
        if include_source_trace:
            unique_sources: set[tuple[str, str]] = set()
            for result in results:
                st = str(result.get("source_type") or "")
                sid = result.get("source_id")
                if sid and st in _traceable_types:
                    unique_sources.add((st, str(sid)))

            for st, sid in unique_sources:
                try:
                    traces_cache[(st, sid)] = AgentRetrievalService.get_source_trace(
                        db,
                        workspace_id=workspace_id,
                        source_type=st,
                        source_id=sid,
                    )
                except Exception:
                    traces_cache[(st, sid)] = None

        evidence: list[dict] = []
        for result in results:
            source_type = str(result.get("source_type") or "")
            source_id = result.get("source_id")

            source_trace: dict | None = None
            if include_source_trace and source_id:
                source_trace = traces_cache.get((source_type, str(source_id)))

            chunk_id = result.get("chunk_id")
            chunk_id_str = str(chunk_id) if chunk_id is not None else None
            facts = result.get("chunk_metadata") or {}

            evidence.append(
                {
                    "content": result.get("chunk_text") or "",
                    "score": float(result.get("score") or 0.0),
                    "source_type": source_type,
                    "source_id": source_id,
                    "chunk_type": result.get("chunk_type") or "",
                    "facts": facts,
                    "citation": build_citation(
                        source_type=source_type,
                        source_id=source_id,
                        chunk_id=chunk_id_str,
                        document_id=facts.get("document_id"),
                        chunk_type=result.get("chunk_type"),
                    ),
                    "source_trace": source_trace,
                }
            )

        return evidence

    @staticmethod
    def _is_matching_risk_result(result: dict, risk_type: str) -> bool:
        if result.get("source_type") != KNOWLEDGE_SOURCE_TYPE_RISK_FINDING:
            return False

        if result.get("chunk_type") == f"risk_{risk_type}":
            return True

        metadata = result.get("chunk_metadata") or {}
        return metadata.get("risk_type") == risk_type

    @staticmethod
    def _get_related_normalized_records(db: Session, workspace_id: UUID, finding: object) -> list:
        primary_id = getattr(finding, "primary_normalized_record_id", None)
        related_ids = getattr(finding, "related_normalized_record_ids", None) or []

        normalized_record_ids = {
            str(primary_id)
            for primary_id in [primary_id]
            if primary_id is not None
        }
        normalized_record_ids.update(str(related_id) for related_id in related_ids if related_id)

        if not normalized_record_ids:
            return []

        workspace_records = NormalizationRepository.get_by_workspace_id(db, workspace_id)
        return [
            record
            for record in workspace_records
            if str(record.id) in normalized_record_ids
        ]

    @staticmethod
    def _get_workspace_finding_by_source_id(
        db: Session,
        *,
        workspace_id: UUID,
        source_id: str,
    ):
        finding = next(
            (
                finding
                for finding in RiskFindingRepository.get_by_workspace_id(db, workspace_id)
                if str(finding.id) == str(source_id)
            ),
            None,
        )
        if finding is None:
            raise AppException(
                message="Source record not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=KNOWLEDGE_SOURCE_NOT_FOUND,
            )
        return finding

    @staticmethod
    def _get_workspace_normalized_record_by_source_id(
        db: Session,
        *,
        workspace_id: UUID,
        source_id: str,
    ):
        record = next(
            (
                record
                for record in NormalizationRepository.get_by_workspace_id(db, workspace_id)
                if str(record.id) == str(source_id)
            ),
            None,
        )
        if record is None:
            raise AppException(
                message="Source record not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=KNOWLEDGE_SOURCE_NOT_FOUND,
            )
        return record

    @staticmethod
    def _resolve_document_metadata(
        db: Session,
        *,
        workspace_id: UUID,
        document_ids: list[str],
    ) -> list[dict]:
        documents: list[dict] = []
        for document_id in document_ids:
            try:
                document_uuid = UUID(str(document_id))
            except ValueError:
                continue

            document = DocumentRepository.get_by_id(db, document_uuid)
            if document is None:
                continue
            if document.workspace_id != workspace_id:
                continue

            documents.append(
                {
                    "document_id": str(document.id),
                    "original_filename": document.original_filename,
                    "document_type": document.document_type,
                    "status": document.status,
                }
            )

        return documents

    @staticmethod
    def _serialize_risk_finding(finding: object) -> dict:
        return {
            "id": str(getattr(finding, "id", "")),
            "workspace_id": str(getattr(finding, "workspace_id", "")),
            "document_id": (
                str(getattr(finding, "document_id"))
                if getattr(finding, "document_id", None) is not None
                else None
            ),
            "primary_normalized_record_id": (
                str(getattr(finding, "primary_normalized_record_id"))
                if getattr(finding, "primary_normalized_record_id", None) is not None
                else None
            ),
            "related_normalized_record_ids": getattr(finding, "related_normalized_record_ids", None),
            "risk_type": getattr(finding, "risk_type", None),
            "severity": getattr(finding, "severity", None),
            "title": getattr(finding, "title", None),
            "description": getattr(finding, "description", None),
            "risk_data": getattr(finding, "risk_data", None),
            "status": getattr(finding, "status", None),
        }

    @staticmethod
    def _serialize_normalized_record(record: object) -> dict:
        return {
            "id": str(getattr(record, "id", "")),
            "workspace_id": str(getattr(record, "workspace_id", "")),
            "document_id": str(getattr(record, "document_id", "")),
            "source_record_id": str(getattr(record, "source_record_id", "")),
            "record_category": getattr(record, "record_category", None),
            "normalized_data": getattr(record, "normalized_data", {}) or {},
            "normalization_status": getattr(record, "normalization_status", None),
            "normalization_confidence": getattr(record, "normalization_confidence", None),
            "normalization_errors": getattr(record, "normalization_errors", None),
        }
