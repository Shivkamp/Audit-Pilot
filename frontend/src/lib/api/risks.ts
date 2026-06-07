import { get, post, patch } from './client'
import type {
  RiskFinding,
  RiskFindingListResponse,
  RiskSummary,
  UpdateRiskFindingStatusRequest,
  RunRiskCheckRequest,
} from '../../types/risk'

export const risksApi = {
  runRiskCheck: (workspaceId: string, data?: RunRiskCheckRequest): Promise<{ job_id?: string }> =>
    post<{ job_id?: string }>(`/workspaces/${workspaceId}/risk-checks/run`, data ?? {}),

  listFindings: (workspaceId: string): Promise<RiskFindingListResponse> =>
    get<RiskFindingListResponse>(`/workspaces/${workspaceId}/risk-findings`),

  listFindingsByDocument: (documentId: string): Promise<RiskFinding[]> =>
    get<RiskFinding[]>(`/documents/${documentId}/risk-findings`),

  getSummary: (workspaceId: string): Promise<RiskSummary> =>
    get<RiskSummary>(`/workspaces/${workspaceId}/risk-summary`),

  updateFindingStatus: (
    findingId: string,
    data: UpdateRiskFindingStatusRequest,
  ): Promise<RiskFinding> =>
    patch<RiskFinding>(`/risk-findings/${findingId}/status`, data),
}
