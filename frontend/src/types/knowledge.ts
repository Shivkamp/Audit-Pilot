export interface KnowledgeChunk {
  id: string
  workspace_id: string
  document_id?: string | null
  source_type: string
  source_id: string
  chunk_type: string
  chunk_text: string
  chunk_metadata?: Record<string, unknown> | null
  embedding_status?: string | null
  created_at: string
  updated_at: string
}

export interface KnowledgeIndexSummary {
  workspace_id: string
  total_chunks: number
  documents_indexed: number
  last_rebuilt_at?: string | null
  by_source_type?: Record<string, number> | null
  by_chunk_type?: Record<string, number> | null
  by_embedding_status?: Record<string, number> | null
}

export interface KnowledgeSearchRequest {
  query: string
  limit?: number
  include_retrieval_debug?: boolean
}

export interface KnowledgeSearchResult {
  chunk_id: string
  score: number
  source_type?: string | null
  source_id?: string | null
  chunk_type?: string | null
  chunk_text: string
  chunk_metadata?: Record<string, unknown> | null
  retrieval_debug?: Record<string, unknown> | null
}

export interface KnowledgeSearchResponse {
  results: KnowledgeSearchResult[]
  query: string
}

export interface KnowledgeChunkListResponse {
  workspace_id: string
  total_records: number
  limit: number
  offset: number
  chunks: KnowledgeChunk[]
}
