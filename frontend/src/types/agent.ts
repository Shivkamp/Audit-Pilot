export type AgentMessageRole = 'user' | 'assistant' | 'system'

export interface AgentMessage {
  role: AgentMessageRole
  content: string
  /** UI-only: marks a failed assistant response so it is never sent to backend */
  _error?: boolean
  /** UI-only: the user message to re-send on retry */
  _retryContent?: string
}

export interface AgentChatRequest {
  message: string
  include_evidence?: boolean
  include_source_trace?: boolean
  max_evidence?: number
}

export interface CitationItem {
  source_type?: string | null
  source_id?: string | null
  chunk_id?: string | null
  chunk_text?: string | null
  document_id?: string | null
  relevance_score?: number | null
}

export interface EvidenceItem {
  chunk_id?: string | null
  chunk_text?: string | null
  source_type?: string | null
  source_id?: string | null
  document_id?: string | null
  score?: number | null
}

export interface SourceTraceItem {
  source_type?: string | null
  source_id?: string | null
  document_id?: string | null
  metadata?: Record<string, unknown> | null
}

export interface AgentChatResponse {
  workspace_id: string
  message: string
  intent?: string | null
  answer: string
  citations?: CitationItem[] | null
  evidence?: EvidenceItem[] | null
  source_traces?: SourceTraceItem[] | null
  warnings?: string[] | null
  confidence?: string | null
  provider?: string | null
  model?: string | null
}

// ─── Agent Retrieval — Request types (match backend Pydantic schemas) ──────────

/** POST /workspaces/{workspace_id}/agent-retrieval/evidence */
export interface AgentEvidenceRequest {
  query: string
  limit?: number
  include_source_trace?: boolean
}

/** POST /workspaces/{workspace_id}/agent-retrieval/risk-evidence */
export interface RiskEvidenceRequest {
  risk_type: string
  query?: string
  limit?: number
  include_source_trace?: boolean
}

// ─── Agent Retrieval — Response types (match backend Pydantic schemas) ─────────

/** Single evidence item returned by backend (matches AgentEvidenceItem schema) */
export interface AgentEvidenceItem {
  content: string
  score: number
  source_type: string
  source_id?: string | null
  chunk_type: string
  facts: Record<string, unknown>
  citation: Record<string, unknown>
  source_trace?: Record<string, unknown> | null
}

/** Backend AgentEvidenceResponse envelope */
export interface AgentEvidenceResponse {
  workspace_id: string
  query?: string | null
  risk_type?: string | null
  limit: number
  evidence: AgentEvidenceItem[]
}

// ─── Frontend normalized view model ────────────────────────────────────────────

/**
 * Frontend view model for rendering evidence in EvidenceCard / EvidenceViewerDrawer.
 * Created by normalizeEvidenceItem() from AgentEvidenceItem or manually
 * constructed records (e.g., from useEvidenceViewer finding context mapping).
 */
export interface EvidenceResult {
  chunk_id?: string | null
  chunk_type?: string | null
  source_type?: string | null
  source_id?: string | null
  document_id?: string | null
  content: string
  score: number
  metadata?: Record<string, unknown> | null
  citation?: Record<string, unknown> | null
  source_trace?: Record<string, unknown> | null
}

// ─── Risk Finding Context ───────────────────────────────────────────────────────

export interface RiskFindingContext {
  workspace_id: string
  risk_finding: Record<string, unknown>
  related_normalized_records: Array<Record<string, unknown>>
  source_trace: Record<string, unknown> | null
}
