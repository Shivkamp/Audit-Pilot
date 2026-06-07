import type { EvidenceResult } from '../../types/agent'

type RawEvidence = Record<string, unknown>

/**
 * Normalizes any evidence-shaped object into a consistent EvidenceResult for rendering.
 *
 * Handles two shapes:
 *  1. AgentEvidenceItem (from backend POST /agent-retrieval/evidence):
 *     source_type, source_id are direct fields; citation/source_trace are objects.
 *  2. Manually constructed EvidenceResult (from useEvidenceViewer finding context):
 *     source_type, source_id are inside metadata.
 *
 * Safe: never throws; missing fields become null/empty string/0.
 */
export function normalizeEvidenceItem(raw: RawEvidence | EvidenceResult): EvidenceResult {
  const r = raw as RawEvidence
  const meta = (r.metadata as RawEvidence | null | undefined) ?? {}
  const citation = (r.citation as RawEvidence | null | undefined) ?? {}

  // source_type: direct field → metadata → citation
  const source_type =
    (r.source_type as string | null | undefined) ??
    (meta.source_type as string | null | undefined) ??
    (citation.source_type as string | null | undefined) ??
    null

  // source_id: direct field → metadata → citation
  const source_id =
    (r.source_id as string | null | undefined) ??
    (meta.source_id as string | null | undefined) ??
    (citation.source_id as string | null | undefined) ??
    null

  // document_id: direct field → citation
  const document_id =
    (r.document_id as string | null | undefined) ??
    (citation.document_id as string | null | undefined) ??
    null

  // chunk_id: direct field → citation
  const chunk_id =
    (r.chunk_id as string | null | undefined) ??
    (citation.chunk_id as string | null | undefined) ??
    null

  const chunk_type = (r.chunk_type as string | null | undefined) ?? null
  const content = (r.content as string | undefined) ?? ''
  const score = typeof r.score === 'number' ? r.score : 0

  return {
    chunk_id,
    chunk_type,
    source_type,
    source_id,
    document_id,
    content,
    score,
    metadata: (r.metadata as RawEvidence | null | undefined) ?? null,
    citation: Object.keys(citation).length > 0 ? citation : null,
    source_trace: (r.source_trace as RawEvidence | null | undefined) ?? null,
  }
}
