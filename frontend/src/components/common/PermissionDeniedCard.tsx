import { Lock } from 'lucide-react'
import { cn } from '../../lib/utils'
import type { WorkspaceRole } from '../../types/workspaceMember'

interface PermissionDeniedCardProps {
  message: string
  requiredRoles?: WorkspaceRole[]
  className?: string
}

/**
 * Inline card for contextual permission-denied states within a page.
 * Use when only a section of a page is locked, not the entire page.
 */
export function PermissionDeniedCard({
  message,
  requiredRoles,
  className,
}: PermissionDeniedCardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-amber-200 bg-amber-50 p-4 flex items-start gap-3',
        className,
      )}
    >
      <Lock className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
      <div>
        <p className="text-sm text-amber-800">{message}</p>
        {requiredRoles && requiredRoles.length > 0 && (
          <p className="text-xs text-amber-600 mt-1">
            Required: <strong>{requiredRoles.join(', ')}</strong>
          </p>
        )}
      </div>
    </div>
  )
}
