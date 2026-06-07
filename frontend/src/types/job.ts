// Active (non-terminal) statuses from backend
export const ACTIVE_JOB_STATUSES = [
  'pending',
  'started',
  'extracting',
  'classifying',
  'normalizing',
  'embedding',
  'running_risk_checks',
] as const

// Terminal statuses
export const TERMINAL_JOB_STATUSES = ['completed', 'failed'] as const

export type ActiveJobStatus = (typeof ACTIVE_JOB_STATUSES)[number]
export type TerminalJobStatus = (typeof TERMINAL_JOB_STATUSES)[number]
export type JobStatus = ActiveJobStatus | TerminalJobStatus
export type JobType = string

export function isActiveJobStatus(status: string): boolean {
  return (ACTIVE_JOB_STATUSES as readonly string[]).includes(status)
}

export interface Job {
  id: string
  workspace_id?: string | null
  document_id?: string | null
  job_type: JobType
  status: JobStatus
  celery_task_id?: string | null
  progress_percent?: number
  current_step?: string | null
  error_message?: string | null
  started_at?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
}
