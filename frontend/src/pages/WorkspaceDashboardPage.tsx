import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Upload,
  ShieldAlert,
  Settings2,
  BookOpen,
  Bot,
  Briefcase,
  Users,
  CalendarDays,
  Clock,
} from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { StatusBadge } from '../components/common/StatusBadge'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { useWorkspace } from '../hooks/useWorkspaces'
import { useAuth } from '../hooks/useAuth'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { formatDate } from '../lib/utils'
import {
  canUploadDocuments,
  canRunRiskCheck,
  canConfigureRiskRules,
  canRebuildKnowledgeIndex,
  canUseAgent,
} from '../lib/auth/permissions'
import { cn } from '../lib/utils'

interface ActionCardProps {
  label: string
  description: string
  icon: React.FC<React.SVGProps<SVGSVGElement>>
  onClick: () => void
  disabled?: boolean
  variant?: 'default' | 'primary'
}

function ActionCard({
  label,
  description,
  icon: Icon,
  onClick,
  disabled,
  variant = 'default',
}: ActionCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'bg-white border rounded-xl p-5 text-left transition-all duration-150 cursor-pointer w-full',
        disabled
          ? 'opacity-50 cursor-not-allowed border-slate-200'
          : variant === 'primary'
            ? 'border-blue-200 hover:border-blue-400 hover:shadow-md'
            : 'border-slate-200 hover:border-slate-300 hover:shadow-card',
      )}
    >
      <div
        className={cn(
          'w-9 h-9 rounded-lg flex items-center justify-center mb-3',
          variant === 'primary' ? 'bg-blue-100' : 'bg-slate-100',
        )}
      >
        <Icon
          className={cn('w-4 h-4', variant === 'primary' ? 'text-blue-600' : 'text-slate-600')}
        />
      </div>
      <p className="text-sm font-semibold text-slate-900">{label}</p>
      <p className="text-xs text-slate-500 mt-0.5">{description}</p>
    </button>
  )
}

export function WorkspaceDashboardPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const navigate = useNavigate()
  const { currentWorkspaceRole, setCurrentWorkspace } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)
  const { data: workspace, isLoading, error, refetch } = useWorkspace(workspaceId)

  // Persist the current workspace and synced role when this page is visited
  useEffect(() => {
    if (workspaceId) setCurrentWorkspace(workspaceId, derivedRole ?? undefined)
  }, [workspaceId, derivedRole, setCurrentWorkspace])

  const role = derivedRole ?? currentWorkspaceRole
  const allowWhenRoleUnknown = (allowed: boolean) => (role == null ? false : allowed)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title={workspace?.name ?? 'Workspace'}
        subtitle={workspace?.description ?? 'Manage documents, risks, and AI analysis'}
      />

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} onRetry={() => refetch()} className="mb-4" />}

      {/* Workspace info card */}
      {!isLoading && !error && workspace && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-card mb-6 flex flex-wrap items-center gap-x-6 gap-y-3">
          {workspace.status && <StatusBadge status={workspace.status} />}
          {workspace.financial_year && (
            <span className="flex items-center gap-1.5 text-sm text-slate-500">
              <CalendarDays className="w-3.5 h-3.5" />
              FY {workspace.financial_year}
            </span>
          )}
          {workspace.assessment_year && (
            <span className="text-sm text-slate-500">AY {workspace.assessment_year}</span>
          )}
          <span className="flex items-center gap-1.5 text-sm text-slate-400 ml-auto">
            <Clock className="w-3.5 h-3.5" />
            Created {formatDate(workspace.created_at)}
          </span>
        </div>
      )}

      {!isLoading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ActionCard
            label="Upload Documents"
            description="Add PDFs, CSVs, and Excel files for processing"
            icon={Upload}
            variant="primary"
            disabled={!allowWhenRoleUnknown(canUploadDocuments(role))}
            onClick={() => navigate(`/workspaces/${workspaceId}/documents`)}
          />
          <ActionCard
            label="Run Risk Check"
            description="Detect TDS mismatches and compliance issues"
            icon={ShieldAlert}
            disabled={!allowWhenRoleUnknown(canRunRiskCheck(role))}
            onClick={() => navigate(`/workspaces/${workspaceId}/risks`)}
          />
          <ActionCard
            label="Configure Risk Rules"
            description="Customize detection thresholds and rules"
            icon={Settings2}
            disabled={!allowWhenRoleUnknown(canConfigureRiskRules(role))}
            onClick={() => navigate(`/workspaces/${workspaceId}/settings`)}
          />
          <ActionCard
            label="Rebuild Knowledge Index"
            description="Re-index documents for search and AI retrieval"
            icon={BookOpen}
            disabled={!allowWhenRoleUnknown(canRebuildKnowledgeIndex(role))}
            onClick={() => navigate(`/workspaces/${workspaceId}/knowledge`)}
          />
          <ActionCard
            label="Ask AI Agent"
            description="Ask questions about your documents and findings"
            icon={Bot}
            variant="primary"
            disabled={!allowWhenRoleUnknown(canUseAgent(role))}
            onClick={() => navigate(`/workspaces/${workspaceId}/agent`)}
          />
          <ActionCard
            label="Processing Jobs"
            description="Monitor document processing status"
            icon={Briefcase}
            onClick={() => navigate(`/workspaces/${workspaceId}/jobs`)}
          />
          <ActionCard
            label="Members"
            description="Manage workspace access and roles"
            icon={Users}
            onClick={() => navigate(`/workspaces/${workspaceId}/members`)}
          />
        </div>
      )}
    </div>
  )
}
