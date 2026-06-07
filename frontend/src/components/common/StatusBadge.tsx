import { cn } from '../../lib/utils'

type StatusValue = string

interface StatusConfig {
  bg: string
  text: string
  dot?: string
  /** Whether to show an animated pulse dot */
  pulse?: boolean
}

const STATUS_MAP: Record<string, StatusConfig> = {
  // Document statuses
  uploaded:   { bg: 'bg-blue-50',   text: 'text-blue-700',   dot: 'bg-blue-400' },
  processing: { bg: 'bg-blue-50',    text: 'text-blue-600',    dot: 'bg-blue-500',   pulse: true },
  processed:  { bg: 'bg-green-50',  text: 'text-green-700',  dot: 'bg-green-500' },
  failed:     { bg: 'bg-red-50',    text: 'text-red-700',    dot: 'bg-red-500' },
  deleted:    { bg: 'bg-slate-100', text: 'text-slate-500' },

  // Job statuses
  pending:           { bg: 'bg-amber-50',   text: 'text-amber-700',  dot: 'bg-amber-400', pulse: true },
  started:           { bg: 'bg-blue-50',     text: 'text-blue-600',    dot: 'bg-blue-500',   pulse: true },
  extracting:        { bg: 'bg-blue-50',    text: 'text-blue-700',   dot: 'bg-blue-500',  pulse: true },
  classifying:       { bg: 'bg-indigo-50',  text: 'text-indigo-700', dot: 'bg-indigo-500', pulse: true },
  normalizing:       { bg: 'bg-violet-50',  text: 'text-violet-700', dot: 'bg-violet-500', pulse: true },
  embedding:         { bg: 'bg-purple-50',  text: 'text-purple-700', dot: 'bg-purple-500', pulse: true },
  running_risk_checks: { bg: 'bg-orange-50', text: 'text-orange-700', dot: 'bg-orange-500', pulse: true },
  completed:         { bg: 'bg-green-50',   text: 'text-green-700',  dot: 'bg-green-500' },

  // Shared / workspace statuses
  active:   { bg: 'bg-green-50',  text: 'text-green-700', dot: 'bg-green-500' },
  inactive: { bg: 'bg-slate-100', text: 'text-slate-500' },
  archived: { bg: 'bg-slate-100', text: 'text-slate-400' },

  // Upload queue statuses
  queued:    { bg: 'bg-slate-100', text: 'text-slate-600' },
  uploading: { bg: 'bg-blue-50',   text: 'text-blue-600', dot: 'bg-blue-500', pulse: true },
  retrying:  { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-400', pulse: true },
  cancelled: { bg: 'bg-slate-100', text: 'text-slate-400' },

  // Risk finding statuses
  open:      { bg: 'bg-red-50',   text: 'text-red-700',   dot: 'bg-red-500' },
  reviewed:  { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-400' },
  resolved:  { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-500' },
  dismissed: { bg: 'bg-slate-100', text: 'text-slate-400' },

  // Fallback
  unknown: { bg: 'bg-slate-100', text: 'text-slate-500' },
}

const STATUS_LABELS: Record<string, string> = {
  uploaded: 'Uploaded',
  processing: 'Processing',
  processed: 'Processed',
  failed: 'Failed',
  deleted: 'Deleted',
  pending: 'Pending',
  started: 'Started',
  extracting: 'Extracting',
  classifying: 'Classifying',
  normalizing: 'Normalizing',
  embedding: 'Embedding',
  running_risk_checks: 'Risk Checks',
  completed: 'Completed',
  active: 'Active',
  inactive: 'Inactive',
  archived: 'Archived',
  queued: 'Queued',
  uploading: 'Uploading',
  retrying: 'Retrying',
  cancelled: 'Cancelled',
  open: 'Open',
  reviewed: 'Reviewed',
  resolved: 'Resolved',
  dismissed: 'Dismissed',
  unknown: 'Unknown',
}

interface StatusBadgeProps {
  status: StatusValue
  className?: string
  /** Show an animated pulse dot for active states */
  showDot?: boolean
}

export function StatusBadge({ status, className, showDot = true }: StatusBadgeProps) {
  const config = STATUS_MAP[status] ?? { bg: 'bg-slate-100', text: 'text-slate-500' }
  const label = STATUS_LABELS[status] ?? status.replace(/_/g, ' ')
  const hasDot = showDot && config.dot

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        config.bg,
        config.text,
        className,
      )}
      aria-label={label}
    >
      {hasDot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full flex-shrink-0',
            config.dot,
            config.pulse && 'motion-safe:animate-pulse-dot',
          )}
          aria-hidden="true"
        />
      )}
      {label}
    </span>
  )
}
