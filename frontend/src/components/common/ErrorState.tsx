import { AlertCircle, RefreshCw } from 'lucide-react'
import { cn } from '../../lib/utils'
import { extractErrorMessage } from '../../lib/utils'

interface ErrorStateProps {
  error?: unknown
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({ error, message, onRetry, className }: ErrorStateProps) {
  const msg = message ?? (error ? extractErrorMessage(error) : 'Something went wrong')

  return (
    <div
      className={cn(
        'rounded-xl border border-red-200 bg-red-50 p-4 flex items-start gap-3',
        className,
      )}
    >
      <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-red-800">Error</p>
        <p className="text-sm text-red-700 mt-0.5">{msg}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 flex items-center gap-1.5 text-xs font-medium text-red-700 hover:text-red-800 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Try again
          </button>
        )}
      </div>
    </div>
  )
}
