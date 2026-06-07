import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { riskRulesApi } from '../lib/api/riskRules'
import type { UpdateRiskRuleConfigRequest, BulkUpdateRiskRuleConfigsRequest } from '../types/riskRule'
import { extractErrorMessage } from '../lib/utils'

export function useRiskRules(workspaceId: string) {
  return useQuery({
    queryKey: ['riskRules', workspaceId],
    queryFn: () => riskRulesApi.list(workspaceId),
    // Extract configs array from paginated envelope for backward compat
    select: (data) => data.configs,
    enabled: !!workspaceId,
  })
}

export function useInitializeRiskRules(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => riskRulesApi.initialize(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['riskRules', workspaceId] })
      toast.success('Risk rules initialized')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useUpdateRiskRule(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      configId,
      data,
    }: {
      configId: string
      data: UpdateRiskRuleConfigRequest
    }) => riskRulesApi.update(configId, data),
    onSuccess: (_, { configId }) => {
      qc.invalidateQueries({ queryKey: ['riskRules', workspaceId] })
      qc.invalidateQueries({ queryKey: ['riskRule', configId] })
      toast.success('Rule configuration saved')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useBulkUpdateRiskRules(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: BulkUpdateRiskRuleConfigsRequest) =>
      riskRulesApi.bulkUpdate(workspaceId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['riskRules', workspaceId] })
      toast.success('All changes saved')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useResetRiskRuleDefaults(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => riskRulesApi.resetDefaults(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['riskRules', workspaceId] })
      toast.success('Risk rules reset to defaults')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
