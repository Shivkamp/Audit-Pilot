import { cn } from '../../lib/utils'
import type { WorkspaceRole } from '../../types/workspaceMember'

const ROLE_COLORS: Record<WorkspaceRole, string> = {
  owner: 'bg-violet-100 text-violet-700',
  admin: 'bg-blue-100 text-blue-600',
  editor: 'bg-amber-100 text-amber-700',
  viewer: 'bg-slate-100 text-slate-600',
}

const ROLE_LABELS: Record<WorkspaceRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  editor: 'Editor',
  viewer: 'Viewer',
}

interface RoleBadgeProps {
  role: WorkspaceRole
  className?: string
}

export function RoleBadge({ role, className }: RoleBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        ROLE_COLORS[role] ?? 'bg-slate-100 text-slate-600',
        className,
      )}
    >
      {ROLE_LABELS[role] ?? role}
    </span>
  )
}
