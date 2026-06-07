import { get, post, patch } from './client'
import type {
  RiskRuleConfig,
  RiskRuleConfigListResponse,
  UpdateRiskRuleConfigRequest,
  BulkUpdateRiskRuleConfigsRequest,
} from '../../types/riskRule'

export const riskRulesApi = {
  initialize: (workspaceId: string): Promise<unknown> =>
    post<unknown>(`/workspaces/${workspaceId}/risk-rule-configs/initialize`),

  // Backend returns paginated envelope { workspace_id, total_records, limit, offset, configs }
  list: (workspaceId: string): Promise<RiskRuleConfigListResponse> =>
    get<RiskRuleConfigListResponse>(`/workspaces/${workspaceId}/risk-rule-configs`),

  get: (configId: string): Promise<RiskRuleConfig> =>
    get<RiskRuleConfig>(`/risk-rule-configs/${configId}`),

  update: (configId: string, data: UpdateRiskRuleConfigRequest): Promise<RiskRuleConfig> =>
    patch<RiskRuleConfig>(`/risk-rule-configs/${configId}`, data),

  // TODO: confirm backend payload shape if it changes; currently { configs: [{ rule_key, ... }] }
  bulkUpdate: (
    workspaceId: string,
    data: BulkUpdateRiskRuleConfigsRequest,
  ): Promise<RiskRuleConfigListResponse> =>
    patch<RiskRuleConfigListResponse>(`/workspaces/${workspaceId}/risk-rule-configs`, data),

  resetDefaults: (workspaceId: string): Promise<unknown> =>
    post<unknown>(`/workspaces/${workspaceId}/risk-rule-configs/reset-defaults`),
}
