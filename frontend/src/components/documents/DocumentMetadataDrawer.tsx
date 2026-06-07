import { X, FileText, HardDrive, Tag, Calendar } from 'lucide-react'
import { useDocument } from '../../hooks/useDocuments'
import { StatusBadge } from '../common/StatusBadge'
import { LoadingSpinner } from '../common/LoadingState'
import { formatDate, formatFileSize } from '../../lib/utils'

interface DocumentMetadataDrawerProps {
  documentId: string | null
  onClose: () => void
}

function MetaRow({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="py-2.5 grid grid-cols-[140px_1fr] gap-3 border-b border-slate-100 last:border-0">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <span className="text-xs text-slate-800 break-all">{value ?? '—'}</span>
    </div>
  )
}

export function DocumentMetadataDrawer({ documentId, onClose }: DocumentMetadataDrawerProps) {
  const { data: document, isLoading } = useDocument(documentId ?? '')

  if (!documentId) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <div
        className="fixed inset-y-0 right-0 w-full max-w-sm bg-white shadow-drawer z-50 flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-label="Document Metadata"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <div className="flex items-center gap-2.5">
            <FileText className="w-4 h-4 text-slate-500" />
            <h2 className="text-sm font-semibold text-slate-900">Document Details</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner />
            </div>
          )}

          {document && (
            <>
              <div className="mb-5">
                <p className="text-sm font-semibold text-slate-900 break-all leading-snug">
                  {document.original_filename}
                </p>
                <div className="mt-1.5">
                  <StatusBadge status={document.status} />
                </div>
              </div>

              {/* File info */}
              <div className="mb-5">
                <div className="flex items-center gap-1.5 mb-2">
                  <HardDrive className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    File
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg px-3 py-1">
                  <MetaRow label="Filename" value={document.original_filename} />
                  <MetaRow label="Extension" value={document.file_extension} />
                  <MetaRow label="Content type" value={document.content_type} />
                  <MetaRow label="File size" value={formatFileSize(document.file_size_bytes)} />
                  <MetaRow label="Storage" value={document.storage_backend} />
                </div>
              </div>

              {/* Classification */}
              <div className="mb-5">
                <div className="flex items-center gap-1.5 mb-2">
                  <Tag className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Classification
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg px-3 py-1">
                  <MetaRow label="Detected type" value={document.document_type} />
                  <MetaRow
                    label="Confidence"
                    value={
                      document.classification_confidence != null
                        ? `${(document.classification_confidence * 100).toFixed(1)}%`
                        : undefined
                    }
                  />
                </div>
              </div>

              {/* Timestamps */}
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Timeline
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg px-3 py-1">
                  <MetaRow label="Uploaded" value={formatDate(document.created_at)} />
                  <MetaRow label="Last updated" value={formatDate(document.updated_at)} />
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
