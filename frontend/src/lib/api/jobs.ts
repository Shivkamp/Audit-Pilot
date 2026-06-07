import { get, post } from './client'
import type { Job } from '../../types/job'

export const jobsApi = {
  listWorkspaceJobs: (workspaceId: string): Promise<Job[]> =>
    get<Job[]>(`/workspaces/${workspaceId}/jobs`),

  listDocumentJobs: (documentId: string): Promise<Job[]> =>
    get<Job[]>(`/documents/${documentId}/jobs`),

  getJob: (jobId: string): Promise<Job> =>
    get<Job>(`/jobs/${jobId}`),

  retryJob: (jobId: string): Promise<Job> =>
    post<Job>(`/jobs/${jobId}/retry`),

  // Aliases for backward compat with existing hooks
  listByWorkspace: (workspaceId: string): Promise<Job[]> =>
    get<Job[]>(`/workspaces/${workspaceId}/jobs`),

  listByDocument: (documentId: string): Promise<Job[]> =>
    get<Job[]>(`/documents/${documentId}/jobs`),

  get: (jobId: string): Promise<Job> =>
    get<Job>(`/jobs/${jobId}`),

  retry: (jobId: string): Promise<Job> =>
    post<Job>(`/jobs/${jobId}/retry`),
}
