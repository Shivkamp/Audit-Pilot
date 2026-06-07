import { ShieldX } from 'lucide-react'
import type { WorkspaceRole } from '../../types/workspaceMember'

interface ForbiddenStateProps {
  title?: string
  message?: string
  requiredRoles?: WorkspaceRole[]
}

export function ForbiddenState({
  title = 'Access Restricted',
  message = "You don't have permission to access this page.",
  requiredRoles,
}: ForbiddenStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-6 text-center">
      <div className="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center mb-4">
        <ShieldX className="w-7 h-7 text-red-500" />
      </div>
      <h2 className="text-xl font-semibold text-slate-800 mb-2">{title}</h2>
      <p className="text-sm text-slate-500 max-w-sm mb-4">{message}</p>
      {requiredRoles && requiredRoles.length > 0 && (
        <p className="text-xs text-slate-400">
          Required role{requiredRoles.length > 1 ? 's' : ''}:{' '}
          <strong className="text-slate-500">{requiredRoles.join(', ')}</strong>
        </p>
      )}
    </div>
  )
}
