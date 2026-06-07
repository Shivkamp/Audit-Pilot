import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { workspacesApi } from '../lib/api/workspaces'
import type { CreateWorkspaceRequest, UpdateWorkspaceRequest } from '../types/workspace'
import { extractErrorMessage } from '../lib/utils'

export function useWorkspaces(clientId: string) {
  return useQuery({
    queryKey: ['workspaces', 'client', clientId],
    queryFn: () => workspacesApi.listByClient(clientId),
    enabled: !!clientId,
  })
}

export function useWorkspace(workspaceId: string) {
  return useQuery({
    queryKey: ['workspaces', workspaceId],
    queryFn: () => workspacesApi.get(workspaceId),
    enabled: !!workspaceId,
  })
}

export function useCreateWorkspace(clientId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateWorkspaceRequest) => workspacesApi.create(clientId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workspaces', 'client', clientId] })
      toast.success('Workspace created successfully')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useUpdateWorkspace(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: UpdateWorkspaceRequest) => workspacesApi.update(workspaceId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workspaces'] })
      toast.success('Workspace updated')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useDeleteWorkspace(clientId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (workspaceId: string) => workspacesApi.delete(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workspaces', 'client', clientId] })
      qc.invalidateQueries({ queryKey: ['workspaces'] })
      toast.success('Workspace archived')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
