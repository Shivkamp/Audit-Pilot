import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { workspaceMembersApi } from '../lib/api/workspaceMembers'
import type { AddMemberRequest, UpdateMemberRoleRequest } from '../types/workspaceMember'
import { extractErrorMessage } from '../lib/utils'

export function useWorkspaceMembers(workspaceId: string) {
  return useQuery({
    queryKey: ['workspaceMembers', workspaceId],
    queryFn: () => workspaceMembersApi.list(workspaceId),
    enabled: !!workspaceId,
    // 403 means viewer can't list members — return empty array instead of throwing
    retry: (failureCount, error: unknown) => {
      const status = (error as { response?: { status?: number } })?.response?.status
      if (status === 403) return false
      return failureCount < 2
    },
  })
}

export function useAddMember(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: AddMemberRequest) => workspaceMembersApi.add(workspaceId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workspaceMembers', workspaceId] })
      qc.invalidateQueries({ queryKey: ['myWorkspaceRole', workspaceId] })
      qc.invalidateQueries({ queryKey: ['workspace', workspaceId] })
      toast.success('Member added successfully')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useUpdateMemberRole(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ memberId, data }: { memberId: string; data: UpdateMemberRoleRequest }) =>
      workspaceMembersApi.updateRole(workspaceId, memberId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workspaceMembers', workspaceId] })
      qc.invalidateQueries({ queryKey: ['myWorkspaceRole', workspaceId] })
      qc.invalidateQueries({ queryKey: ['workspace', workspaceId] })
      toast.success('Member role updated')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useRemoveMember(workspaceId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (memberId: string) => workspaceMembersApi.remove(workspaceId, memberId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workspaceMembers', workspaceId] })
      qc.invalidateQueries({ queryKey: ['myWorkspaceRole', workspaceId] })
      qc.invalidateQueries({ queryKey: ['workspace', workspaceId] })
      toast.success('Member removed')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
