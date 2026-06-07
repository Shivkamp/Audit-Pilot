import { get, post, del } from './client'
import type {
  KnowledgeChunkListResponse,
  KnowledgeIndexSummary,
  KnowledgeSearchRequest,
  KnowledgeSearchResponse,
} from '../../types/knowledge'

export const knowledgeApi = {
  rebuildIndex: (workspaceId: string): Promise<{ job_id?: string }> =>
    post<{ job_id?: string }>(`/workspaces/${workspaceId}/knowledge-index/rebuild`),

  getIndexSummary: (workspaceId: string): Promise<KnowledgeIndexSummary> =>
    get<KnowledgeIndexSummary>(`/workspaces/${workspaceId}/knowledge-index/summary`),

  search: (workspaceId: string, data: KnowledgeSearchRequest): Promise<KnowledgeSearchResponse> =>
    post<KnowledgeSearchResponse>(`/workspaces/${workspaceId}/knowledge-search`, data),

  listChunks: (workspaceId: string): Promise<KnowledgeChunkListResponse> =>
    get<KnowledgeChunkListResponse>(`/workspaces/${workspaceId}/knowledge-chunks`),

  deleteIndex: (workspaceId: string): Promise<void> =>
    del<void>(`/workspaces/${workspaceId}/knowledge-index`),
}
