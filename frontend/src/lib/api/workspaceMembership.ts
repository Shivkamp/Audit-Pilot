import { get } from './client'
import type { WorkspaceRole } from '../../types/workspaceMember'

export interface WorkspaceMembership {
  workspace_id: string
  user_id: string
  role: WorkspaceRole
  permissions: Record<string, boolean>
}

export const workspaceMembershipApi = {
  getMyMembership: (workspaceId: string): Promise<WorkspaceMembership> =>
    get<WorkspaceMembership>(`/workspaces/${workspaceId}/my-membership`),
}
