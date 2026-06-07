import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { clientsApi } from '../lib/api/clients'
import type { CreateClientRequest, UpdateClientRequest } from '../types/client'
import { extractErrorMessage } from '../lib/utils'

export function useClients() {
  return useQuery({
    queryKey: ['clients'],
    queryFn: clientsApi.list,
  })
}

export function useClient(clientId: string) {
  return useQuery({
    queryKey: ['clients', clientId],
    queryFn: () => clientsApi.get(clientId),
    enabled: !!clientId,
  })
}

export function useCreateClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateClientRequest) => clientsApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clients'] })
      toast.success('Client created successfully')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useUpdateClient(clientId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: UpdateClientRequest) => clientsApi.update(clientId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clients'] })
      toast.success('Client updated')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}

export function useDeleteClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (clientId: string) => clientsApi.delete(clientId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clients'] })
      toast.success('Client deleted')
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  })
}
