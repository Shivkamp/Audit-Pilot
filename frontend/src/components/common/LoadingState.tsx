import { cn } from '../../lib/utils'

interface LoadingStateProps {
  className?: string
  rows?: number
}

export function LoadingState({ className, rows = 4 }: LoadingStateProps) {
  return (
    <div className={cn('space-y-3 p-6', className)} aria-label="Loading…" aria-busy="true">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-3 items-center">
          <div className="shimmer h-4 rounded w-1/4" />
          <div className="shimmer h-4 rounded w-1/3" />
          <div className="shimmer h-4 rounded flex-1" />
        </div>
      ))}
    </div>
  )
}

export function LoadingSpinner({ className }: { className?: string }) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn(
        'w-5 h-5 border-2 border-slate-200 border-t-blue-600 rounded-full animate-spin',
        className,
      )}
    />
  )
}

export function PageLoadingState() {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3" aria-busy="true">
      <LoadingSpinner className="w-8 h-8" />
      <span className="text-sm text-slate-500">Loading…</span>
    </div>
  )
}

/**
 * Full-page shimmer skeleton for dashboard-like pages.
 */
export function DashboardLoadingState() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6" aria-busy="true" aria-label="Loading dashboard…">
      {/* Header shimmer */}
      <div className="space-y-2">
        <div className="shimmer h-7 w-56 rounded-lg" />
        <div className="shimmer h-4 w-80 rounded" />
      </div>
      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
            <div className="shimmer w-10 h-10 rounded-xl" />
            <div className="shimmer h-7 w-1/2 rounded-lg" />
            <div className="shimmer h-3 w-2/3 rounded" />
          </div>
        ))}
      </div>
      {/* Content blocks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 space-y-3">
          <div className="shimmer h-5 w-40 rounded" />
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="shimmer h-10 w-full rounded-lg" />
          ))}
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
          <div className="shimmer h-5 w-32 rounded" />
          <div className="shimmer h-4 w-full rounded" />
          <div className="shimmer h-4 w-3/4 rounded" />
          <div className="shimmer h-4 w-1/2 rounded" />
        </div>
      </div>
    </div>
  )
}
