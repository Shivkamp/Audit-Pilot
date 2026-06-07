import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { knowledgeApi } from '../lib/api/knowledge'
import type { KnowledgeSearchRequest } from '../types/knowledge'
import { extractErrorMessage } from '../lib/utils'

export function useKnowledgeSearch(workspaceId: string) {
  const mutation = useMutation({
    mutationFn: (req: KnowledgeSearchRequest) => knowledgeApi.search(workspaceId, req),
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
  return mutation
}
