import { cn } from '../../lib/utils'

interface ShimmerBlockProps {
  className?: string
}

/**
 * Single shimmer block — a loading placeholder.
 * Uses CSS shimmer animation (reduced-motion: static bg, no animation).
 */
export function ShimmerBlock({ className }: ShimmerBlockProps) {
  return (
    <div
      className={cn(
        'shimmer rounded',
        className,
      )}
      aria-hidden="true"
    />
  )
}

interface ShimmerCardProps {
  className?: string
}

/**
 * Full card skeleton shimmer.
 */
export function ShimmerCard({ className }: ShimmerCardProps) {
  return (
    <div
      className={cn(
        'bg-white border border-slate-200 rounded-xl p-5 shadow-card space-y-3',
        className,
      )}
      aria-hidden="true"
    >
      <div className="flex items-center gap-3">
        <ShimmerBlock className="w-10 h-10 rounded-xl" />
        <div className="flex-1 space-y-1.5">
          <ShimmerBlock className="h-4 w-1/2" />
          <ShimmerBlock className="h-3 w-1/3" />
        </div>
      </div>
      <ShimmerBlock className="h-7 w-1/3 rounded-lg" />
      <ShimmerBlock className="h-3 w-2/3" />
    </div>
  )
}

interface ShimmerTableRowProps {
  cols?: number
}

/**
 * Shimmer table row skeleton.
 */
export function ShimmerTableRow({ cols = 5 }: ShimmerTableRowProps) {
  return (
    <tr aria-hidden="true">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <ShimmerBlock
            className={cn(
              'h-3.5 rounded',
              i === 0 ? 'w-32' : i === cols - 1 ? 'w-16' : 'w-full max-w-[160px]',
            )}
          />
        </td>
      ))}
    </tr>
  )
}

interface ShimmerTableProps {
  rows?: number
  cols?: number
}

/**
 * Full shimmer table body.
 */
export function ShimmerTable({ rows = 5, cols = 5 }: ShimmerTableProps) {
  return (
    <tbody aria-label="Loading…">
      {Array.from({ length: rows }).map((_, i) => (
        <ShimmerTableRow key={i} cols={cols} />
      ))}
    </tbody>
  )
}

interface ShimmerListProps {
  rows?: number
  className?: string
}

/**
 * Shimmer list of text rows (for search results, etc.).
 */
export function ShimmerList({ rows = 4, className }: ShimmerListProps) {
  return (
    <div className={cn('space-y-3', className)} aria-label="Loading…">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 space-y-2">
          <ShimmerBlock className="h-4 w-3/4" />
          <ShimmerBlock className="h-3 w-full" />
          <ShimmerBlock className="h-3 w-5/6" />
          <div className="flex gap-2 pt-1">
            <ShimmerBlock className="h-5 w-16 rounded-full" />
            <ShimmerBlock className="h-5 w-20 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  )
}
