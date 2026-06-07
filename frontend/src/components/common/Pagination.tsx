import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '../../lib/utils'

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100]

interface PaginationProps {
  /** 1-indexed current page */
  page: number
  pageSize: number
  totalItems: number
  pageSizeOptions?: number[]
  onPageChange: (page: number) => void
  onPageSizeChange: (pageSize: number) => void
  className?: string
}

export function Pagination({
  page,
  pageSize,
  totalItems,
  pageSizeOptions = PAGE_SIZE_OPTIONS,
  onPageChange,
  onPageSizeChange,
  className,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))
  const start = totalItems === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, totalItems)

  const canPrev = page > 1
  const canNext = page < totalPages

  return (
    <div className={cn('flex flex-wrap items-center justify-between gap-3 py-3', className)}>
      {/* Count info */}
      <p className="text-xs text-slate-500">
        {totalItems === 0
          ? 'No items'
          : `Showing ${start}–${end} of ${totalItems}`}
      </p>

      <div className="flex items-center gap-3">
        {/* Page size selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-slate-500">Rows</span>
          <select
            value={pageSize}
            onChange={(e) => {
              onPageSizeChange(Number(e.target.value))
            }}
            className="text-xs border border-slate-200 rounded-lg px-2 py-1 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
          >
            {pageSizeOptions.map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>

        {/* Page navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={!canPrev}
            aria-label="Previous page"
            className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="text-xs text-slate-600 px-1 min-w-[60px] text-center">
            {page} / {totalPages}
          </span>

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={!canNext}
            aria-label="Next page"
            className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
