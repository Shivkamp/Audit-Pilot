import { cn } from '../../lib/utils'
import type { WorkspaceRole } from '../../types/workspaceMember'

interface RoleRequiredNoticeProps {
  requiredRoles: WorkspaceRole[]
  className?: string
}

/**
 * Small inline notice showing which roles are required for an action.
 * Use next to disabled buttons or restricted controls.
 */
export function RoleRequiredNotice({ requiredRoles, className }: RoleRequiredNoticeProps) {
  return (
    <span
      className={cn('text-xs text-slate-400 italic', className)}
      aria-live="polite"
    >
      Requires: {requiredRoles.join(' / ')}
    </span>
  )
}
