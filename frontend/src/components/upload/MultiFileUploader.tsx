import { useCallback, useRef, useState } from 'react'
import { Upload, FolderOpen, Trash2 } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { documentsApi } from '../../lib/api/documents'
import { UploadQueueItem } from './UploadQueueItem'
import type { UploadQueueItemState, UploadStatus } from './UploadQueueItem'
import { ACCEPTED_FILE_EXTENSIONS } from '../../lib/constants'
import { extractErrorMessage } from '../../lib/utils'

const ACCEPTED_EXTENSIONS = ['.pdf', '.csv', '.xlsx', '.xls']

function validateExtension(filename: string): boolean {
  const lower = filename.toLowerCase()
  return ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext))
}

function getExtension(filename: string): string {
  const idx = filename.lastIndexOf('.')
  return idx >= 0 ? filename.slice(idx).toLowerCase() : ''
}

let _idCounter = 0
function newId() {
  _idCounter += 1
  return `upload-${Date.now()}-${_idCounter}`
}

interface MultiFileUploaderProps {
  workspaceId: string
  onUploadComplete?: () => void
}

export function MultiFileUploader({ workspaceId, onUploadComplete }: MultiFileUploaderProps) {
  const [queue, setQueue] = useState<UploadQueueItemState[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const qc = useQueryClient()

  const updateItem = useCallback((id: string, patch: Partial<UploadQueueItemState>) => {
    setQueue((prev) => prev.map((item) => (item.id === id ? { ...item, ...patch } : item)))
  }, [])

  const addFiles = useCallback((files: File[]) => {
    const newItems: UploadQueueItemState[] = []
    const rejected: string[] = []

    for (const file of files) {
      if (!validateExtension(file.name)) {
        rejected.push(file.name)
        continue
      }
      // Deduplicate by name + size + lastModified
      const isDupe = queue.some(
        (q) =>
          q.fileName === file.name && q.size === file.size,
      )
      if (isDupe) continue

      newItems.push({
        id: newId(),
        file,
        fileName: file.name,
        size: file.size,
        extension: getExtension(file.name),
        status: 'queued',
      })
    }

    if (rejected.length > 0) {
      toast.error(
        `Unsupported file type${rejected.length > 1 ? 's' : ''}: ${rejected.join(', ')}. Accepted: ${ACCEPTED_FILE_EXTENSIONS}`,
      )
    }

    if (newItems.length > 0) {
      setQueue((prev) => [...prev, ...newItems])
    }
  }, [queue])

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files))
      e.target.value = ''
    }
  }

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setIsDragOver(false)
      addFiles(Array.from(e.dataTransfer.files))
    },
    [addFiles],
  )

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = () => setIsDragOver(false)

  const removeItem = (id: string) => {
    setQueue((prev) => prev.filter((item) => item.id !== id))
  }

  const uploadOne = async (item: UploadQueueItemState, status: UploadStatus) => {
    updateItem(item.id, { status, errorMessage: undefined })
    try {
      const result = await documentsApi.uploadWorkspaceDocument(workspaceId, item.file)
      updateItem(item.id, {
        status: 'uploaded',
        documentId: result.document.id,
        jobId: result.processing_job.id,
      })
      qc.invalidateQueries({ queryKey: ['documents', workspaceId] })
      qc.invalidateQueries({ queryKey: ['jobs', workspaceId] })
      return true
    } catch (err) {
      updateItem(item.id, {
        status: 'failed',
        errorMessage: extractErrorMessage(err),
      })
      return false
    }
  }

  const handleUploadAll = async () => {
    const toUpload = queue.filter(
      (item) => item.status === 'queued' || item.status === 'failed',
    )
    if (toUpload.length === 0) return

    setIsUploading(true)
    let uploaded = 0
    let failed = 0

    for (const item of toUpload) {
      const ok = await uploadOne(item, 'uploading')
      if (ok) uploaded += 1
      else failed += 1
    }

    setIsUploading(false)

    if (failed === 0) {
      toast.success(`Uploaded ${uploaded} file${uploaded !== 1 ? 's' : ''}. Processing started.`)
    } else {
      toast.error(
        `Uploaded ${uploaded}, failed ${failed}. Failed files can be retried individually.`,
      )
    }

    onUploadComplete?.()
  }

  const handleRetryItem = async (id: string) => {
    const item = queue.find((q) => q.id === id)
    if (!item) return
    setIsUploading(true)
    await uploadOne(item, 'retrying')
    setIsUploading(false)
    qc.invalidateQueries({ queryKey: ['documents', workspaceId] })
    qc.invalidateQueries({ queryKey: ['jobs', workspaceId] })
  }

  const handleClearQueue = () => {
    const hasActiveOrFailed = queue.some(
      (item) => item.status === 'uploading' || item.status === 'retrying',
    )
    if (hasActiveOrFailed) {
      if (!confirm('Upload is in progress. Clear all completed and failed items?')) return
    }
    setQueue((prev) => prev.filter((item) => item.status === 'uploading' || item.status === 'retrying'))
  }

  const pendingCount = queue.filter((q) => q.status === 'queued' || q.status === 'failed').length
  const hasItems = queue.length > 0

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-card overflow-hidden">
      {/* Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`relative flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed rounded-t-xl transition-all duration-150 cursor-pointer ${
          isDragOver
            ? 'border-blue-400 bg-blue-50 shadow-[0_0_0_4px_rgba(37,99,235,0.1),0_0_24px_rgba(37,99,235,0.12)] ring-0'
            : 'border-slate-200 bg-slate-50 hover:bg-slate-100 hover:border-slate-300'
        }`}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Click or drag files to upload"
        onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
      >
        <Upload
          className={`w-8 h-8 transition-colors ${isDragOver ? 'text-blue-500' : 'text-slate-300'}`}
        />
        <div className="text-center">
          <p className="text-sm font-medium text-slate-700">
            Drop files here, or{' '}
            <span className="text-blue-600 underline underline-offset-2">browse</span>
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Accepted: PDF, CSV, XLSX, XLS
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ACCEPTED_FILE_EXTENSIONS}
          className="sr-only"
          onChange={handleFileInputChange}
          aria-hidden="true"
        />
      </div>

      {/* Queue */}
      {hasItems && (
        <>
          <ul className="divide-y divide-slate-100 max-h-64 overflow-y-auto">
            {queue.map((item) => (
              <UploadQueueItem
                key={item.id}
                item={item}
                onRemove={removeItem}
                onRetry={handleRetryItem}
                isUploading={isUploading}
              />
            ))}
          </ul>

          {/* Actions bar */}
          <div className="flex items-center justify-between gap-3 px-4 py-3 bg-slate-50 border-t border-slate-200">
            <button
              onClick={handleClearQueue}
              disabled={isUploading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear Queue
            </button>

            <button
              onClick={handleUploadAll}
              disabled={isUploading || pendingCount === 0}
              className="flex items-center gap-2 px-4 py-1.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FolderOpen className="w-4 h-4" />
              {isUploading
                ? 'Uploading…'
                : `Upload All${pendingCount > 0 ? ` (${pendingCount})` : ''}`}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
