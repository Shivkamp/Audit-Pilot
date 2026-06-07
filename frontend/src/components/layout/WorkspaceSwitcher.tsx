import { useNavigate } from 'react-router-dom'
import { FolderOpen } from 'lucide-react'
import { useWorkspace } from '../../hooks/useWorkspaces'

interface WorkspaceSwitcherProps {
  workspaceId?: string
}

export function WorkspaceSwitcher({ workspaceId }: WorkspaceSwitcherProps) {
  const navigate = useNavigate()
  const { data: workspace } = useWorkspace(workspaceId ?? '')

  if (!workspaceId) {
    return (
      <button
        onClick={() => navigate('/clients')}
        className="flex items-center gap-1.5 px-2.5 py-1.5 text-sm text-slate-500 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors duration-150 cursor-pointer"
      >
        <FolderOpen className="w-3.5 h-3.5 flex-shrink-0" />
        <span className="font-medium">Select workspace</span>
      </button>
    )
  }

  return (
    <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-blue-50 border border-blue-100">
      <div className="w-5 h-5 rounded-md bg-blue-600 flex items-center justify-center flex-shrink-0">
        <FolderOpen className="w-3 h-3 text-white" />
      </div>
      <span className="text-sm font-semibold text-blue-900 truncate max-w-[180px]">
        {workspace?.name ?? 'Loading…'}
      </span>
    </div>
  )
}
