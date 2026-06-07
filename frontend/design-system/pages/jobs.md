# Jobs Page — Design Override
Inherits from `design-system/MASTER.md`.

## Route
`/workspaces/:workspaceId/jobs`

## Page Header
- Title: "Processing Jobs"
- Subtitle dynamic:
  - `hasActiveJobs = true` → "Auto-refreshing while jobs are active"
  - else → "Monitor document extraction and processing status"
- Right action: Refresh icon button (slate)

## Polling Behaviour
- `useJobsPolling(workspaceId)` → `refetchInterval: hasActiveJobs ? 3000 : false`
- `isActiveJobStatus()` from `types/job.ts` covers ALL non-terminal statuses

## Permission Notice
- Viewers (canRetryJobs = false) see `PermissionDeniedCard` at top with:
  - Message: "You can view processing jobs, but only owner, admin, or editor can retry failed jobs."
  - requiredRoles: ['owner', 'admin', 'editor']
- Notice appears ABOVE the table, not instead of it

## Jobs Table
- Columns: Job ID, Type (hidden md), Status, Stage/Progress (hidden lg), Started (hidden md), Completed (hidden xl), Actions
- Job ID: 8-char prefix in mono xs, followed by truncated error_message in text-red-600 if `status === 'failed'`
- Type: job_type with `_` replaced by spaces
- Stage: `current_step` with `_` replaced by spaces + `(N%)` if progress_percent > 0
- Actions: FileText icon link to /documents page (if document_id set), Retry button (only for failed + canRetry)

## Retry Button
- Size: xs, outline, amber variant
- Only shown when `job.status === 'failed' && canRetryJobs(role)`
- Calls `jobsApi.retryJob(jobId)`, then invalidates `['jobs', workspaceId]` and `['job', jobId]`
- Success toast: "Job retry queued"

## Empty State
- Icon: `Briefcase`
- Title: "No processing jobs yet"
- Body: "Upload documents to start processing jobs."

## Job Status Colors (via StatusBadge)
| Status | Badge |
|--------|-------|
| pending | slate |
| started, extracting, classifying, normalizing, embedding | sky (animated?) |
| running_risk_checks | blue |
| completed | green |
| failed | red |
