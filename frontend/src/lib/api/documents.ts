import { get, del, apiClient } from './client'
import type { Document, DocumentDownloadUrlResponse, UploadDocumentResponse } from '../../types/document'

export const documentsApi = {
  // Fetch all documents for a workspace
  listWorkspaceDocuments: (workspaceId: string): Promise<Document[]> =>
    get<Document[]>(`/workspaces/${workspaceId}/documents`),

  // Upload one file — field name is `file` as expected by backend
  uploadWorkspaceDocument: (workspaceId: string, file: File): Promise<UploadDocumentResponse> => {
    const form = new FormData()
    form.append('file', file)
    return apiClient
      .post<{ data: UploadDocumentResponse }>(`/workspaces/${workspaceId}/documents/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data.data)
  },

  getDocument: (documentId: string): Promise<Document> =>
    get<Document>(`/documents/${documentId}`),

  deleteDocument: (documentId: string): Promise<void> =>
    del<void>(`/documents/${documentId}`),

  // Returns download_url field from backend DocumentDownloadUrlResponse
  getDocumentDownloadUrl: (documentId: string): Promise<DocumentDownloadUrlResponse> =>
    get<DocumentDownloadUrlResponse>(`/documents/${documentId}/download-url`),
}
