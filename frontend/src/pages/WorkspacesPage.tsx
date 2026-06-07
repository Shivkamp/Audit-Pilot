import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { FolderOpen, Plus, Pencil, Archive, ArrowLeft, RefreshCw } from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { StatusBadge } from '../components/common/StatusBadge'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { WorkspaceForm, type WorkspaceFormData } from '../components/workspaces/WorkspaceForm'
import { useWorkspaces, useCreateWorkspace, useUpdateWorkspace, useDeleteWorkspace } from '../hooks/useWorkspaces'
import { useClient } from '../hooks/useClients'
import { useAuth } from '../hooks/useAuth'
import { formatDate } from '../lib/utils'
import type { Workspace } from '../types/workspace'

export function WorkspacesPage() {
  const { clientId = '' } = useParams<{ clientId: string }>()
  const navigate = useNavigate()
  const { currentWorkspaceId, setCurrentWorkspace } = useAuth()
  const { data: client } = useClient(clientId)
  const { data: workspaces, isLoading, error, refetch } = useWorkspaces(clientId)

  const [showCreate, setShowCreate] = useState(false)
  const [editTarget, setEditTarget] = useState<Workspace | null>(null)
  const [archiveTarget, setArchiveTarget] = useState<Workspace | null>(null)

  const createMutation = useCreateWorkspace(clientId)
  const updateMutation = useUpdateWorkspace(editTarget?.id ?? '')
  const deleteMutation = useDeleteWorkspace(clientId)

  const handleCreate = (data: WorkspaceFormData) => {
    createMutation.mutate(
      {
        name: data.name.trim(),
        financial_year: data.financial_year.trim(),
      },
      { onSuccess: () => setShowCreate(false) },
    )
  }

  const handleUpdate = (data: WorkspaceFormData) => {
    if (!editTarget) return
    updateMutation.mutate(
      {
        name: data.name.trim(),
        financial_year: data.financial_year.trim(),
      },
      { onSuccess: () => setEditTarget(null) },
    )
  }

  const handleArchive = () => {
    if (!archiveTarget) return
    const archivedWorkspaceId = archiveTarget.id
    deleteMutation.mutate(archivedWorkspaceId, {
      onSuccess: () => {
        if (currentWorkspaceId === archivedWorkspaceId) {
          setCurrentWorkspace(null)
        }
        setArchiveTarget(null)
      },
    })
  }

  const handleOpen = (ws: Workspace) => {
    setCurrentWorkspace(ws.id)
    navigate(`/workspaces/${ws.id}`)
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Back link */}
      <div className="mb-4">
        <Link
          to="/clients"
          className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Clients
        </Link>
      </div>

      <PageHeader
        title={client ? `${client.name}` : 'Workspaces'}
        subtitle="Select or create a workspace to start auditing"
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
              New Workspace
            </button>
          </div>
        }
      />

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} onRetry={() => refetch()} className="mb-4" />}

      {!isLoading && !error && workspaces?.length === 0 && (
        <EmptyState
          icon={<FolderOpen className="w-12 h-12" />}
          title="No workspaces yet"
          body="Create a workspace to start uploading documents and running risk checks."
          action={
            <button
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer"
              onClick={() => setShowCreate(true)}
            >
              <Plus className="w-4 h-4" />
              New Workspace
            </button>
          }
        />
      )}

      {!isLoading && workspaces && workspaces.length > 0 && (
        <div className="overflow-hidden border border-slate-200 rounded-xl bg-white shadow-card">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Name
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">
                  FY
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">
                  AY
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">
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
              {workspaces.map((ws) => (
                <tr key={ws.id} className="hover:bg-slate-50 transition-colors duration-100">
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleOpen(ws)}
                      className="text-sm font-semibold text-blue-600 hover:text-blue-700 cursor-pointer text-left"
                    >
                      {ws.name}
                    </button>
                    {ws.description && (
                      <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{ws.description}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 hidden sm:table-cell">
                    {ws.financial_year ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 hidden sm:table-cell">
                    {ws.assessment_year ?? '—'}
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    {ws.status ? <StatusBadge status={ws.status} /> : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 hidden lg:table-cell">
                    {formatDate(ws.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => setEditTarget(ws)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"
                        title="Edit workspace"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setArchiveTarget(ws)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-amber-50 hover:text-amber-600 transition-colors cursor-pointer"
                        title="Archive workspace"
                      >
                        <Archive className="w-3.5 h-3.5" />
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
      <WorkspaceForm
        open={showCreate}
        isLoading={createMutation.isPending}
        onClose={() => setShowCreate(false)}
        onSubmit={handleCreate}
      />

      {/* Edit modal */}
      <WorkspaceForm
        open={!!editTarget}
        defaultValues={
          editTarget
            ? {
                name: editTarget.name,
                financial_year: editTarget.financial_year ?? '',
                assessment_year: editTarget.assessment_year ?? '',
              }
            : undefined
        }
        isLoading={updateMutation.isPending}
        onClose={() => setEditTarget(null)}
        onSubmit={handleUpdate}
      />

      {/* Archive confirm */}
      <ConfirmDialog
        open={!!archiveTarget}
        title="Archive Workspace"
        description={`Are you sure you want to archive "${archiveTarget?.name}"? The workspace and its data will be retained but marked inactive.`}
        confirmLabel="Archive"
        variant="danger"
        isLoading={deleteMutation.isPending}
        onConfirm={handleArchive}
        onCancel={() => setArchiveTarget(null)}
      />
    </div>
  )
}