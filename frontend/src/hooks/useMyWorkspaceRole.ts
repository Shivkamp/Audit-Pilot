import type { WorkspaceRole } from '../types/workspaceMember'
import { useMyWorkspaceMembership } from './useMyWorkspaceMembership'

/**
 * Returns the current user's role in the given workspace via /my-membership.
 * Handles 403/404 gracefully — returns undefined without throwing.
 */
export function useMyWorkspaceRole(workspaceId: string | null | undefined): {
  role: WorkspaceRole | undefined
  isLoading: boolean
} {
  const { data: membership, isLoading } = useMyWorkspaceMembership(workspaceId)

  return {
    role: membership?.role,
    isLoading,
  }
}
