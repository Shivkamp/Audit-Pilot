export type ClientStatus = 'active' | 'inactive' | string

export interface Client {
  id: string
  name: string
  pan?: string | null
  gstin?: string | null
  description?: string | null
  status?: ClientStatus
  created_at: string
  updated_at: string
}

export interface CreateClientRequest {
  name: string
  pan?: string
  gstin?: string
  description?: string
}

export interface UpdateClientRequest {
  name?: string
  pan?: string
  gstin?: string
  description?: string
}
