import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { knowledgeApi } from '../lib/api/knowledge'
import { extractErrorMessage } from '../lib/utils'

export function useKnowledgeIndexSummary(workspaceId: string) {
  return useQuery({
    queryKey: ['knowledgeIndexSummary', workspaceId],
    queryFn: () => knowledgeApi.getIndexSummary(workspaceId),
    enabled: !!workspaceId,
  })
}

export function useKnowledgeChunks(workspaceId: string) {
  return useQuery({
    queryKey: ['knowledgeChunks', workspaceId],
    queryFn: () => knowledgeApi.listChunks(workspaceId),
    select: (data) => data.chunks,
    enabled: !!workspaceId,
  })
}

export function useRebuildKnowledgeIndex(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => knowledgeApi.rebuildIndex(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['knowledgeIndexSummary', workspaceId] })
      qc.invalidateQueries({ queryKey: ['knowledgeChunks', workspaceId] })
      toast.success('Knowledge index rebuild started')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useDeleteKnowledgeIndex(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => knowledgeApi.deleteIndex(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['knowledgeIndexSummary', workspaceId] })
      qc.invalidateQueries({ queryKey: ['knowledgeChunks', workspaceId] })
      toast.success('Knowledge index deleted')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
