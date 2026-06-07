import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { documentsApi } from '../lib/api/documents'
import { extractErrorMessage } from '../lib/utils'

export function useDocuments(workspaceId: string) {
  return useQuery({
    queryKey: ['documents', workspaceId],
    queryFn: () => documentsApi.listWorkspaceDocuments(workspaceId),
    enabled: !!workspaceId,
  })
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => documentsApi.getDocument(documentId),
    enabled: !!documentId,
  })
}

export function useDeleteDocument(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (documentId: string) => documentsApi.deleteDocument(documentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents', workspaceId] })
      qc.invalidateQueries({ queryKey: ['jobs', workspaceId] })
      toast.success('Document deleted')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
