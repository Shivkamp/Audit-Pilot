import { get, post, patch, del } from './client'
import type {
  WorkspaceMember,
  AddMemberRequest,
  UpdateMemberRoleRequest,
} from '../../types/workspaceMember'

export const workspaceMembersApi = {
  list: (workspaceId: string): Promise<WorkspaceMember[]> =>
    get<WorkspaceMember[]>(`/workspaces/${workspaceId}/members`),

  add: (workspaceId: string, data: AddMemberRequest): Promise<WorkspaceMember> =>
    post<WorkspaceMember>(`/workspaces/${workspaceId}/members`, data),

  updateRole: (
    workspaceId: string,
    memberId: string,
    data: UpdateMemberRoleRequest,
  ): Promise<WorkspaceMember> =>
    patch<WorkspaceMember>(`/workspaces/${workspaceId}/members/${memberId}`, data),

  remove: (workspaceId: string, memberId: string): Promise<void> =>
    del<void>(`/workspaces/${workspaceId}/members/${memberId}`),
}
