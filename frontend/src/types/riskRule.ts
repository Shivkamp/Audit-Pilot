import type { RiskSeverity } from './risk'

export interface RiskRuleConfig {
  id: string
  workspace_id: string
  rule_key: string
  risk_type: string
  is_enabled: boolean
  severity: RiskSeverity
  threshold_amount?: number | null
  threshold_percent?: number | null
  config_data?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface RiskRuleConfigListResponse {
  workspace_id: string
  total_records: number
  limit: number
  offset: number
  configs: RiskRuleConfig[]
}

export interface UpdateRiskRuleConfigRequest {
  is_enabled?: boolean
  severity?: string
  threshold_amount?: number | null
  threshold_percent?: number | null
  config_data?: Record<string, unknown> | null
}

// Bulk update — uses rule_key as identifier (backend schema)
export interface BulkUpdateRiskRuleConfigItem {
  rule_key: string
  is_enabled?: boolean | null
  severity?: string | null
  threshold_amount?: number | null
  threshold_percent?: number | null
  config_data?: Record<string, unknown> | null
}

export interface BulkUpdateRiskRuleConfigsRequest {
  configs: BulkUpdateRiskRuleConfigItem[]
}
