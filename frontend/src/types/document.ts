export type DocumentStatus = 'uploaded' | 'processing' | 'processed' | 'failed' | 'deleted'

export interface Document {
  id: string
  workspace_id: string
  original_filename: string
  stored_filename: string
  file_extension: string
  content_type?: string | null
  file_size_bytes: number
  storage_backend: string
  document_type: string
  classification_confidence?: number | null
  status: DocumentStatus
  created_at: string
  updated_at: string
}

export interface ProcessingJobSummary {
  id: string
  status: string
  job_type: string
}

export interface UploadDocumentResponse {
  document: Document
  processing_job: ProcessingJobSummary
}

export interface DocumentDownloadUrlResponse {
  document_id: string
  download_url: string
  expires_in_seconds: number
}
