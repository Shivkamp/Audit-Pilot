import { get, post } from './client'
import type {
  AgentEvidenceRequest,
  AgentEvidenceResponse,
  RiskEvidenceRequest,
  RiskFindingContext,
} from '../../types/agent'

export const agentRetrievalApi = {
  getEvidence: (workspaceId: string, data: AgentEvidenceRequest): Promise<AgentEvidenceResponse> =>
    post<AgentEvidenceResponse>(`/workspaces/${workspaceId}/agent-retrieval/evidence`, data),

  getRiskEvidence: (
    workspaceId: string,
    data: RiskEvidenceRequest,
  ): Promise<AgentEvidenceResponse> =>
    post<AgentEvidenceResponse>(`/workspaces/${workspaceId}/agent-retrieval/risk-evidence`, data),

  getRiskFindingContext: (
    workspaceId: string,
    riskFindingId: string,
  ): Promise<RiskFindingContext> =>
    get<RiskFindingContext>(
      `/workspaces/${workspaceId}/agent-retrieval/risk-findings/${riskFindingId}/context`,
    ),

  getSourceTrace: (
    workspaceId: string,
    sourceType: string,
    sourceId: string,
  ): Promise<unknown> =>
    get<unknown>(`/workspaces/${workspaceId}/source-trace/${sourceType}/${sourceId}`),
}
