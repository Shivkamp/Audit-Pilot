import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FileText, FileSpreadsheet, Download, Trash2, Info, Briefcase, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { StatusBadge } from '../components/common/StatusBadge'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { PermissionDeniedCard } from '../components/common/PermissionDeniedCard'
import { MultiFileUploader } from '../components/upload/MultiFileUploader'
import { DocumentMetadataDrawer } from '../components/documents/DocumentMetadataDrawer'
import { useDocuments, useDeleteDocument } from '../hooks/useDocuments'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { useAuth } from '../hooks/useAuth'
import { canUploadDocuments, canDeleteDocuments } from '../lib/auth/permissions'
import { documentsApi } from '../lib/api/documents'
import { formatDate, formatFileSize } from '../lib/utils'
import type { Document } from '../types/document'

function FileIcon({ extension }: { extension?: string }) {
  const ext = (extension ?? '').toLowerCase()
  if (ext === '.pdf') return <FileText className="w-4 h-4 text-red-400 flex-shrink-0" />
  if (ext === '.csv') return <FileSpreadsheet className="w-4 h-4 text-green-500 flex-shrink-0" />
  if (ext === '.xlsx' || ext === '.xls')
    return <FileSpreadsheet className="w-4 h-4 text-emerald-500 flex-shrink-0" />
  return <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
}

export function DocumentsPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const navigate = useNavigate()
  const { currentWorkspaceRole } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)

  // Prefer the role from the dedicated hook; fall back to auth context
  const role = derivedRole ?? currentWorkspaceRole

  const { data: documents, isLoading, error, refetch } = useDocuments(workspaceId)
  const deleteMutation = useDeleteDocument(workspaceId)

  const [deleteTarget, setDeleteTarget] = useState<Document | null>(null)
  const [metaDocumentId, setMetaDocumentId] = useState<string | null>(null)

  const canUpload = canUploadDocuments(role)
  const canDelete = canDeleteDocuments(role)

  const handleDownload = async (documentId: string, filename: string) => {
    try {
      const res = await documentsApi.getDocumentDownloadUrl(documentId)
      window.open(res.download_url, '_blank', 'noopener,noreferrer')
    } catch {
      toast.error(`Could not get download URL for ${filename}`)
    }
  }

  const handleDeleteConfirm = () => {
    if (!deleteTarget) return
    deleteMutation.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
    })
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title="Documents"
        subtitle="Upload and manage your audit documents"
        actions={
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Refresh documents"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        }
      />

      {/* Upload Section */}
      <div className="mb-6">
        {canUpload ? (
          <MultiFileUploader workspaceId={workspaceId} onUploadComplete={() => refetch()} />
        ) : (
          <PermissionDeniedCard
            message="You can view documents, but your current workspace role does not allow uploading files."
            requiredRoles={['owner', 'admin', 'editor']}
          />
        )}
      </div>

      {/* Document list */}
      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} onRetry={() => refetch()} className="mb-4" />}

      {!isLoading && !error && documents?.length === 0 && (
        <EmptyState
          icon={<FileText className="w-12 h-12" />}
          title="No documents uploaded yet"
          body="Upload your first document above to start processing and risk analysis."
        />
      )}

      {!isLoading && documents && documents.length > 0 && (
        <div className="overflow-hidden border border-slate-200 rounded-xl bg-white shadow-card">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">File</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Size</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Detected Type</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Uploaded</th>
                <th scope="col" className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50 transition-colors duration-100">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <FileIcon extension={doc.file_extension} />
                      <div className="min-w-0">
                        <p className="font-medium text-slate-900 truncate max-w-[200px]">
                          {doc.original_filename}
                        </p>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">{doc.id.slice(0, 8)}…</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 hidden sm:table-cell">
                    {formatFileSize(doc.file_size_bytes)}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-600 hidden md:table-cell">
                    {doc.document_type && doc.document_type !== 'unknown'
                      ? doc.document_type
                      : <span className="text-slate-400">—</span>}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={doc.status} />
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 hidden lg:table-cell">
                    {formatDate(doc.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => handleDownload(doc.id, doc.original_filename)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-blue-700 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                        title="Download"
                        aria-label={`Download ${doc.original_filename}`}
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setMetaDocumentId(doc.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                        title="View metadata"
                        aria-label={`View metadata for ${doc.original_filename}`}
                      >
                        <Info className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => navigate(`/workspaces/${workspaceId}/jobs`)}
                        className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                        title="View processing jobs"
                        aria-label="View processing jobs"
                      >
                        <Briefcase className="w-3.5 h-3.5" />
                      </button>
                      {canDelete && (
                        <button
                          onClick={() => setDeleteTarget(doc)}
                          className="p-1.5 rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-red-500"
                          title="Delete document"
                          aria-label={`Delete ${doc.original_filename}`}
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <DocumentMetadataDrawer
        documentId={metaDocumentId}
        onClose={() => setMetaDocumentId(null)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Document"
        description={`Are you sure you want to delete "${deleteTarget?.original_filename}"? This cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        isLoading={deleteMutation.isPending}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
