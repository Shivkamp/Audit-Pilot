import { cn } from '../../lib/utils'
import type { RiskSeverity } from '../../types/risk'

interface SeverityConfig {
  bg: string
  text: string
  border: string
  dot: string
  /** Ring for critical */
  ring?: string
}

const SEVERITY_MAP: Record<RiskSeverity, SeverityConfig> = {
  critical: {
    bg: 'bg-red-50',
    text: 'text-red-800',
    border: 'border-red-200',
    dot: 'bg-red-600',
    ring: 'ring-1 ring-red-300',
  },
  high: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    dot: 'bg-red-500',
  },
  medium: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    dot: 'bg-amber-500',
  },
  low: {
    bg: 'bg-green-50',
    text: 'text-green-700',
    border: 'border-green-200',
    dot: 'bg-green-500',
  },
  info: {
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    border: 'border-blue-200',
    dot: 'bg-blue-500',
  },
}

const SEVERITY_LABELS: Record<RiskSeverity, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  info: 'Info',
}

interface SeverityBadgeProps {
  severity: RiskSeverity
  className?: string
  /** Size variant */
  size?: 'sm' | 'md'
}

export function SeverityBadge({ severity, className, size = 'sm' }: SeverityBadgeProps) {
  const config = SEVERITY_MAP[severity] ?? {
    bg: 'bg-slate-100',
    text: 'text-slate-500',
    border: 'border-slate-200',
    dot: 'bg-slate-400',
  }
  const label = SEVERITY_LABELS[severity] ?? severity

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-semibold rounded-full border',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm',
        config.bg,
        config.text,
        config.border,
        config.ring,
        className,
      )}
    >
      <span
        className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', config.dot)}
        aria-hidden="true"
      />
      {label}
    </span>
  )
}
