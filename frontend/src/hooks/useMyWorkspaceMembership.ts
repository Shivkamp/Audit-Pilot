import { useQuery } from '@tanstack/react-query'
import { workspaceMembershipApi } from '../lib/api/workspaceMembership'
import { useAuth } from './useAuth'

export function useMyWorkspaceMembership(workspaceId: string | null | undefined) {
  const { currentUser } = useAuth()

  return useQuery({
    queryKey: ['myWorkspaceMembership', workspaceId],
    queryFn: () => workspaceMembershipApi.getMyMembership(workspaceId!),
    enabled: !!workspaceId && !!currentUser,
    staleTime: 60_000,
    retry: (failureCount, error: unknown) => {
      const status = (error as { response?: { status?: number } })?.response?.status
      if (status === 403 || status === 404) return false
      return failureCount < 2
    },
  })
}
