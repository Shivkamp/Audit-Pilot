import type { ReactNode } from 'react'
import { Lock } from 'lucide-react'
import type { WorkspaceRole } from '../../types/workspaceMember'
import { cn } from '../../lib/utils'

interface PermissionGateProps {
  role: WorkspaceRole | null | undefined
  allowed: WorkspaceRole[]
  fallback?: ReactNode
  children?: ReactNode
  className?: string
}

export function PermissionGate({
  role,
  allowed,
  fallback,
  children,
  className,
}: PermissionGateProps) {
  if (role && allowed.includes(role)) return <>{children}</>

  if (fallback !== undefined) return <>{fallback}</>

  return (
    <div className={cn('rounded-xl border border-slate-200 bg-slate-50 p-4 flex items-center gap-3', className)}>
      <Lock className="w-4 h-4 text-slate-400 flex-shrink-0" />
      <p className="text-sm text-slate-500">
        You need <strong>{allowed.join(' or ')}</strong> role to perform this action.
      </p>
    </div>
  )
}
