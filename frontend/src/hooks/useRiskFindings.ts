import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { risksApi } from '../lib/api/risks'
import type { UpdateRiskFindingStatusRequest } from '../types/risk'
import { extractErrorMessage } from '../lib/utils'

export function useRiskFindings(workspaceId: string) {
  return useQuery({
    queryKey: ['riskFindings', workspaceId],
    queryFn: () => risksApi.listFindings(workspaceId),
    select: (data) => data.findings,
    enabled: !!workspaceId,
  })
}

export function useRiskSummary(workspaceId: string) {
  return useQuery({
    queryKey: ['riskSummary', workspaceId],
    queryFn: () => risksApi.getSummary(workspaceId),
    enabled: !!workspaceId,
  })
}

export function useRunRiskCheck(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => risksApi.runRiskCheck(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['riskFindings', workspaceId] })
      qc.invalidateQueries({ queryKey: ['riskSummary', workspaceId] })
      toast.success('Risk check started')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useUpdateRiskFindingStatus(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      findingId,
      data,
    }: {
      findingId: string
      data: UpdateRiskFindingStatusRequest
    }) => risksApi.updateFindingStatus(findingId, data),
    onSuccess: (_, { findingId }) => {
      qc.invalidateQueries({ queryKey: ['riskFindings', workspaceId] })
      qc.invalidateQueries({ queryKey: ['riskSummary', workspaceId] })
      qc.invalidateQueries({ queryKey: ['riskFinding', findingId] })
      toast.success('Finding status updated')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
