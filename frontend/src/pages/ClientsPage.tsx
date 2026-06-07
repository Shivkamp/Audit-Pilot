import { useState } from 'react'
import { Building2, Plus, Pencil, Trash2, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { StatusBadge } from '../components/common/StatusBadge'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { ClientForm, type ClientFormData } from '../components/clients/ClientForm'
import { useClients, useCreateClient, useUpdateClient, useDeleteClient } from '../hooks/useClients'
import { formatDate } from '../lib/utils'
import type { Client } from '../types/client'

export function ClientsPage() {
  const navigate = useNavigate()
  const { data: clients, isLoading, error, refetch } = useClients()

  const [showCreate, setShowCreate] = useState(false)
  const [editTarget, setEditTarget] = useState<Client | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Client | null>(null)

  const createMutation = useCreateClient()
  const updateMutation = useUpdateClient(editTarget?.id ?? '')
  const deleteMutation = useDeleteClient()

  const normalizeOptionalCode = (value?: string) => {
    const normalized = value?.trim().toUpperCase()
    return normalized ? normalized : undefined
  }

  const handleCreate = (data: ClientFormData) => {
    createMutation.mutate(
      {
        name: data.name.trim(),
        pan: normalizeOptionalCode(data.pan),
        gstin: normalizeOptionalCode(data.gstin),
      },
      { onSuccess: () => setShowCreate(false) },
    )
  }

  const handleUpdate = (data: ClientFormData) => {
    if (!editTarget) return
    updateMutation.mutate(
      {
        name: data.name.trim(),
        pan: normalizeOptionalCode(data.pan),
        gstin: normalizeOptionalCode(data.gstin),
      },
      { onSuccess: () => setEditTarget(null) },
    )
  }

  const handleDelete = () => {
    if (!deleteTarget) return
    deleteMutation.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
    })
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title="Clients"
        subtitle="Manage your audit clients"
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={() => refetch()}
              className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors cursor-pointer"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              onClick={() => setShowCreate(true)}
            >
              <Plus className="w-4 h-4" />
              New Client
            </button>
          </div>
        }
      />

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} onRetry={() => refetch()} className="mb-4" />}

      {!isLoading && !error && clients?.length === 0 && (
        <EmptyState
          icon={<Building2 className="w-12 h-12" />}
          title="No clients yet"
          body="Create your first client to start organizing workspaces and audits."
          action={
            <button
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer"
              onClick={() => setShowCreate(true)}
            >
              <Plus className="w-4 h-4" />
              New Client
            </button>
          }
        />
      )}

      {!isLoading && clients && clients.length > 0 && (
        <div className="overflow-hidden border border-slate-200 rounded-xl bg-white shadow-card">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Name
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">
                  PAN
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">
                  GSTIN
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">
                  Status
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">
                  Created
                </th>
                <th scope="col" className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {clients.map((client) => (
                <tr key={client.id} className="hover:bg-slate-50 transition-colors duration-100">
                  <td className="px-4 py-3">
                    <button
                      onClick={() => navigate(`/clients/${client.id}/workspaces`)}
                      className="text-sm font-semibold text-blue-600 hover:text-blue-700 cursor-pointer text-left"
                    >
                      {client.name}
                    </button>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 hidden sm:table-cell font-mono">
                    {client.pan ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 hidden md:table-cell font-mono">
                    {client.gstin ?? '—'}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    {client.status ? <StatusBadge status={client.status} /> : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 hidden lg:table-cell">
                    {formatDate(client.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => setEditTarget(client)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"
                        title="Edit client"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(client)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer"
                        title="Deactivate client"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create modal */}
      <ClientForm
        open={showCreate}
        isLoading={createMutation.isPending}
        onClose={() => setShowCreate(false)}
        onSubmit={handleCreate}
      />

      {/* Edit modal */}
      <ClientForm
        open={!!editTarget}
        defaultValues={editTarget ? { name: editTarget.name, pan: editTarget.pan ?? '', gstin: editTarget.gstin ?? '' } : undefined}
        isLoading={updateMutation.isPending}
        onClose={() => setEditTarget(null)}
        onSubmit={handleUpdate}
      />

      {/* Deactivate confirm */}
      <ConfirmDialog
        open={!!deleteTarget}
        title="Deactivate Client"
        description={`Are you sure you want to deactivate "${deleteTarget?.name}"? This action can be reversed by an administrator.`}
        confirmLabel="Deactivate"
        variant="danger"
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}