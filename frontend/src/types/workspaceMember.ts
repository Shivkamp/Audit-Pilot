export type WorkspaceRole = 'owner' | 'admin' | 'editor' | 'viewer'

export interface WorkspaceMember {
  id: string
  workspace_id: string
  user_id: string
  role: WorkspaceRole
  user?: import('./user').User
  created_at: string
  updated_at: string
}

export interface AddMemberRequest {
  email: string
  role: WorkspaceRole
}

export interface UpdateMemberRoleRequest {
  role: WorkspaceRole
}
