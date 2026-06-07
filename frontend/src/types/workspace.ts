export type WorkspaceStatus = 'active' | 'archived' | string

export interface Workspace {
  id: string
  client_id: string
  name: string
  financial_year?: string | null
  assessment_year?: string | null
  description?: string | null
  status?: WorkspaceStatus
  created_at: string
  updated_at: string
}

export interface CreateWorkspaceRequest {
  name: string
  financial_year?: string
  assessment_year?: string
  description?: string
}

export interface UpdateWorkspaceRequest {
  name?: string
  financial_year?: string
  assessment_year?: string
  description?: string
}
