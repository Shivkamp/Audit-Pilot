import { useParams, useNavigate } from 'react-router-dom'
import { Briefcase, RotateCcw, RefreshCw, FileText } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { StatusBadge } from '../components/common/StatusBadge'
import { PermissionDeniedCard } from '../components/common/PermissionDeniedCard'
import { useJobsPolling } from '../hooks/useJobsPolling'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { useAuth } from '../hooks/useAuth'
import { canRetryJobs } from '../lib/auth/permissions'
import { jobsApi } from '../lib/api/jobs'
import { extractErrorMessage, formatDateTime } from '../lib/utils'
import { isActiveJobStatus } from '../types/job'

export function JobsPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { currentWorkspaceRole } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)
  const role = derivedRole ?? currentWorkspaceRole

  const { data: jobs, isLoading, error, refetch } = useJobsPolling(workspaceId)

  const canRetry = canRetryJobs(role)

  const hasActiveJobs = jobs?.some((j) => isActiveJobStatus(j.status)) ?? false

  const handleRetry = async (jobId: string) => {
    try {
      await jobsApi.retryJob(jobId)
      qc.invalidateQueries({ queryKey: ['jobs', workspaceId] })
      qc.invalidateQueries({ queryKey: ['job', jobId] })
      toast.success('Job retry queued')
    } catch (err) {
      toast.error(extractErrorMessage(err) ?? 'Could not retry job')
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title="Processing Jobs"
        subtitle={
          hasActiveJobs
            ? 'Auto-refreshing while jobs are active'
            : 'Monitor document extraction and processing status'
        }
        actions={
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Refresh jobs"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        }
      />

      {!canRetry && role !== null && (
        <PermissionDeniedCard
          message="You can view processing jobs, but only owner, admin, or editor can retry failed jobs."
          requiredRoles={['owner', 'admin', 'editor']}
          className="mb-4"
        />
      )}

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} onRetry={() => refetch()} className="mb-4" />}

      {!isLoading && !error && jobs?.length === 0 && (
        <EmptyState
          icon={<Briefcase className="w-12 h-12" />}
          title="No processing jobs yet"
          body="Upload documents to start processing jobs."
        />
      )}

      {!isLoading && jobs && jobs.length > 0 && (
        <div className="overflow-hidden border border-slate-200 rounded-xl bg-white shadow-card">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Job ID</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Type</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Stage</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Started</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden xl:table-cell">Completed</th>
                <th scope="col" className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-slate-50 transition-colors duration-100">
                  <td className="px-4 py-3">
                    <p className="font-mono text-xs text-slate-600">{job.id.slice(0, 8)}…</p>
                    {job.error_message && (
                      <p className="text-xs text-red-600 mt-0.5 max-w-[200px] truncate" title={job.error_message}>
                        {job.error_message}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-600 hidden md:table-cell">
                    {job.job_type.replace(/_/g, ' ')}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={job.status} />
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 hidden lg:table-cell">
                    {job.current_step
                      ? job.current_step.replace(/_/g, ' ')
                      : <span className="text-slate-300">—</span>}
                    {job.progress_percent != null && job.progress_percent > 0 && (
                      <span className="ml-1 text-blue-600">({job.progress_percent}%)</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 hidden md:table-cell">
                    {job.started_at ? formatDateTime(job.started_at) : <span className="text-slate-300">—</span>}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 hidden xl:table-cell">
                    {job.completed_at ? formatDateTime(job.completed_at) : <span className="text-slate-300">—</span>}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      {/* View document */}
                      {job.document_id && (
                        <button
                          onClick={() => navigate(`/workspaces/${workspaceId}/documents`)}
                          className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                          title="View documents"
                          aria-label="View documents"
                        >
                          <FileText className="w-3.5 h-3.5" />
                        </button>
                      )}

                      {/* Retry — only for failed jobs, only if permitted */}
                      {job.status === 'failed' && canRetry && (
                        <button
                          onClick={() => handleRetry(job.id)}
                          className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-400"
                          aria-label="Retry this job"
                        >
                          <RotateCcw className="w-3 h-3" />
                          Retry
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
    </div>
  )
}
