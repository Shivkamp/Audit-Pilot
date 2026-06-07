import { get, post, patch, del } from './client'
import type { Client, CreateClientRequest, UpdateClientRequest } from '../../types/client'

export const clientsApi = {
  list: (): Promise<Client[]> =>
    get<Client[]>('/clients'),

  create: (data: CreateClientRequest): Promise<Client> =>
    post<Client>('/clients', data),

  get: (clientId: string): Promise<Client> =>
    get<Client>(`/clients/${clientId}`),

  update: (clientId: string, data: UpdateClientRequest): Promise<Client> =>
    patch<Client>(`/clients/${clientId}`, data),

  delete: (clientId: string): Promise<void> =>
    del<void>(`/clients/${clientId}`),
}
