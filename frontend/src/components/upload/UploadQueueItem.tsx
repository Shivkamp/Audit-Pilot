import { FileText, FileSpreadsheet, X, RotateCcw, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { StatusBadge } from '../common/StatusBadge'
import { formatFileSize } from '../../lib/utils'

export type UploadStatus =
  | 'queued'
  | 'validating'
  | 'uploading'
  | 'uploaded'
  | 'failed'
  | 'retrying'
  | 'removed'

export interface UploadQueueItemState {
  id: string
  file: File
  fileName: string
  size: number
  extension: string
  status: UploadStatus
  errorMessage?: string
  documentId?: string
  jobId?: string
}

function FileTypeIcon({ extension }: { extension: string }) {
  const ext = extension.toLowerCase().replace('.', '')
  if (ext === 'pdf') return <FileText className="w-4 h-4 text-red-500 flex-shrink-0" />
  if (ext === 'csv') return <FileSpreadsheet className="w-4 h-4 text-green-600 flex-shrink-0" />
  if (ext === 'xlsx' || ext === 'xls')
    return <FileSpreadsheet className="w-4 h-4 text-emerald-600 flex-shrink-0" />
  return <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
}

function StatusIcon({ status }: { status: UploadStatus }) {
  if (status === 'uploading' || status === 'retrying')
    return <Loader2 className="w-4 h-4 text-blue-700 animate-spin flex-shrink-0" />
  if (status === 'uploaded')
    return <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
  if (status === 'failed')
    return <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
  return null
}

interface UploadQueueItemProps {
  item: UploadQueueItemState
  onRemove: (id: string) => void
  onRetry: (id: string) => void
  isUploading: boolean
}

export function UploadQueueItem({ item, onRemove, onRetry, isUploading }: UploadQueueItemProps) {
  const isActive = item.status === 'uploading' || item.status === 'retrying'
  const isDone = item.status === 'uploaded'
  const isFailed = item.status === 'failed'
  const isRemovable = !isActive

  return (
    <li className="flex items-center gap-3 px-4 py-3 border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors">
      <FileTypeIcon extension={item.extension} />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900 truncate">{item.fileName}</p>
        <p className="text-xs text-slate-500 mt-0.5">
          {formatFileSize(item.size)}{' '}
          {item.errorMessage && (
            <span className="text-red-600 ml-1">{item.errorMessage}</span>
          )}
        </p>
      </div>

      <StatusIcon status={item.status} />

      <StatusBadge status={item.status} />

      {isFailed && !isUploading && (
        <button
          onClick={() => onRetry(item.id)}
          className="p-1 rounded text-amber-600 hover:bg-amber-50 transition-colors cursor-pointer"
          title="Retry upload"
          aria-label={`Retry upload for ${item.fileName}`}
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      )}

      {isRemovable && !isDone && (
        <button
          onClick={() => onRemove(item.id)}
          className="p-1 rounded text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"
          title="Remove from queue"
          aria-label={`Remove ${item.fileName} from queue`}
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </li>
  )
}
