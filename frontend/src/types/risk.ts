export type RiskSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info'
export type RiskFindingStatus = 'open' | 'reviewed' | 'resolved' | 'dismissed'

export interface RiskFinding {
  id: string
  workspace_id: string
  document_id?: string | null
  primary_normalized_record_id?: string | null
  related_normalized_record_ids?: string[] | null
  risk_type: string
  severity: RiskSeverity
  title: string
  description?: string | null
  risk_data?: Record<string, unknown> | null
  status: RiskFindingStatus
  created_at: string
  updated_at: string
}

export interface RiskSummary {
  total: number
  critical: number
  high: number
  medium: number
  low: number
  info: number
  open: number
  reviewed: number
  resolved: number
  dismissed: number
}

export interface UpdateRiskFindingStatusRequest {
  status: RiskFindingStatus
}

export interface RunRiskCheckRequest {
  document_ids?: string[]
}

export interface RiskFindingListResponse {
  workspace_id: string
  total_records: number
  limit: number
  offset: number
  findings: RiskFinding[]
}
