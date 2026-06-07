import { useAuth } from '../app/AuthContext'
import { useWorkspace } from './useWorkspaces'

/**
 * Returns the currently selected workspace object.
 * Reads workspaceId from AuthContext (persisted in localStorage),
 * then fetches workspace details via TanStack Query.
 */
export function useCurrentWorkspace() {
  const { currentWorkspaceId } = useAuth()
  const query = useWorkspace(currentWorkspaceId ?? '')
  return {
    workspaceId: currentWorkspaceId,
    workspace: query.data ?? null,
    isLoading: !!currentWorkspaceId && query.isLoading,
  }
}
