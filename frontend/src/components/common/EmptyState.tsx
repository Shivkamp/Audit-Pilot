import type { ReactNode } from 'react'
import { cn } from '../../lib/utils'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  body?: string
  action?: ReactNode
  className?: string
}

export function EmptyState({ icon, title, body, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-16 px-6 text-center animate-fade-in',
        className,
      )}
    >
      {icon && (
        <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 mb-5">
          {icon}
        </div>
      )}
      <p className="text-base font-semibold text-slate-700 mb-1.5 text-balance">{title}</p>
      {body && (
        <p className="text-sm text-slate-500 mb-6 max-w-sm leading-relaxed">{body}</p>
      )}
      {action}
    </div>
  )
}
