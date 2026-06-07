import { useQuery } from '@tanstack/react-query'
import { jobsApi } from '../lib/api/jobs'
import { POLLING_INTERVAL_MS } from '../lib/constants'
import { isActiveJobStatus } from '../types/job'

export function useJobsPolling(workspaceId: string, enabled = true) {
  return useQuery({
    queryKey: ['jobs', workspaceId],
    queryFn: () => jobsApi.listWorkspaceJobs(workspaceId),
    enabled: !!workspaceId && enabled,
    refetchInterval: (query) => {
      const jobs = query.state.data
      if (!jobs) return false
      const hasActive = jobs.some((j) => isActiveJobStatus(j.status))
      return hasActive ? POLLING_INTERVAL_MS : false
    },
  })
}

export function useJob(jobId: string) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.getJob(jobId),
    enabled: !!jobId,
  })
}

export function useDocumentJobs(documentId: string) {
  return useQuery({
    queryKey: ['documentJobs', documentId],
    queryFn: () => jobsApi.listDocumentJobs(documentId),
    enabled: !!documentId,
  })
}
