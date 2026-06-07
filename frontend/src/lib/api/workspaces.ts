import { get, post, patch, del } from './client'
import type { Workspace, CreateWorkspaceRequest, UpdateWorkspaceRequest } from '../../types/workspace'

export const workspacesApi = {
  create: (clientId: string, data: CreateWorkspaceRequest): Promise<Workspace> =>
    post<Workspace>(`/clients/${clientId}/workspaces`, data),

  listByClient: (clientId: string): Promise<Workspace[]> =>
    get<Workspace[]>(`/clients/${clientId}/workspaces`),

  get: (workspaceId: string): Promise<Workspace> =>
    get<Workspace>(`/workspaces/${workspaceId}`),

  update: (workspaceId: string, data: UpdateWorkspaceRequest): Promise<Workspace> =>
    patch<Workspace>(`/workspaces/${workspaceId}`, data),

  delete: (workspaceId: string): Promise<void> =>
    del<void>(`/workspaces/${workspaceId}`),
}
