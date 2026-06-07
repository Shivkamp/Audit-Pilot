import { useNavigate } from 'react-router-dom'
import {
  Building2,
  FolderOpen,
  FileText,
  ShieldAlert,
  Bot,
  ArrowRight,
  CalendarDays,
  ChevronRight,
} from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { StatusBadge } from '../components/common/StatusBadge'
import { AnimatedCounter } from '../components/common/AnimatedCounter'
import { StaggerList, StaggerItem } from '../components/common/StaggerList'
import { useClients } from '../hooks/useClients'
import { useAuth } from '../hooks/useAuth'
import { useCurrentWorkspace } from '../hooks/useCurrentWorkspace'
import { useDocuments } from '../hooks/useDocuments'
import { useRiskFindings } from '../hooks/useRiskFindings'

interface StatCardProps {
  label: string
  value: number | string | undefined | null
  icon: React.FC<React.SVGProps<SVGSVGElement>>
  iconBg: string
  iconColor: string
  onClick?: () => void
  delay?: number
}

function StatCard({ label, value, icon: Icon, iconBg, iconColor, onClick, delay = 0 }: StatCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-white border border-slate-200 rounded-xl p-5 shadow-card text-left hover:border-blue-300 hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-150 cursor-pointer w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 motion-safe:animate-slide-in-up"
      style={{ animationDelay: `${delay}ms`, animationFillMode: 'both' }}
    >
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${iconBg} mb-3`}>
        <Icon className={`w-5 h-5 ${iconColor}`} />
      </div>
      <p className="text-2xl font-bold text-slate-900 tabular-nums">
        <AnimatedCounter value={typeof value === 'number' ? value : undefined} placeholder={value == null ? '—' : String(value)} />
      </p>
      <p className="text-sm text-slate-500 mt-0.5 font-medium">{label}</p>
    </button>
  )
}

export function DashboardPage() {
  const navigate = useNavigate()
  const { currentUser, currentWorkspaceId } = useAuth()
  const { data: clients } = useClients()
  const { workspace } = useCurrentWorkspace()
  const { data: documents } = useDocuments(currentWorkspaceId ?? '')
  const { data: riskFindings } = useRiskFindings(currentWorkspaceId ?? '')

  const greeting = currentUser?.full_name
    ? `Welcome back, ${currentUser.full_name.split(' ')[0]}`
    : 'Welcome back'

  const recentClients = clients?.slice(0, 5) ?? []

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title={greeting}
        subtitle="Here's an overview of your AuditPilot workspace."
      />

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Clients"
          value={clients?.length ?? undefined}
          icon={Building2}
          iconBg="bg-blue-50"
          iconColor="text-blue-600"
          onClick={() => navigate('/clients')}
          delay={0}
        />
        <StatCard
          label="Current Workspace"
          value={workspace?.name ? 1 : undefined}
          icon={FolderOpen}
          iconBg="bg-teal-50"
          iconColor="text-teal-600"
          onClick={() => currentWorkspaceId ? navigate(`/workspaces/${currentWorkspaceId}`) : navigate('/clients')}
          delay={60}
        />
        <StatCard
          label="Documents"
          value={documents?.length}
          icon={FileText}
          iconBg="bg-amber-50"
          iconColor="text-amber-600"
          onClick={() =>
            currentWorkspaceId
              ? navigate(`/workspaces/${currentWorkspaceId}/documents`)
              : navigate('/clients')
          }
          delay={120}
        />
        <StatCard
          label="Risk Findings"
          value={riskFindings?.length}
          icon={ShieldAlert}
          iconBg="bg-red-50"
          iconColor="text-red-600"
          onClick={() =>
            currentWorkspaceId
              ? navigate(`/workspaces/${currentWorkspaceId}/risks`)
              : navigate('/clients')
          }
          delay={180}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Recent Clients */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-800">Recent Clients</h2>
            <button
              onClick={() => navigate('/clients')}
              className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors cursor-pointer"
            >
              View all →
            </button>
          </div>
          {recentClients.length === 0 ? (
            <div className="px-5 py-10 text-center">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-3">
                <Building2 className="w-6 h-6 text-slate-400" />
              </div>
              <p className="text-sm font-semibold text-slate-700 mb-1">No clients yet</p>
              <p className="text-sm text-slate-500 mb-4">Get started by adding your first client.</p>
              <button
                onClick={() => navigate('/clients')}
                className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 cursor-pointer"
              >
                Create your first client
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <StaggerList as="ul" className="divide-y divide-slate-100">
              {recentClients.map((client) => (
                <StaggerItem key={client.id}>
                  <button
                    onClick={() => navigate(`/clients/${client.id}/workspaces`)}
                    className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-slate-50 transition-colors cursor-pointer text-left group"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-800 group-hover:text-blue-700 transition-colors">{client.name}</p>
                      {client.pan && (
                        <p className="text-xs text-slate-400 mt-0.5 font-mono">PAN: {client.pan}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      {client.status && <StatusBadge status={client.status} />}
                      <ChevronRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-400 transition-colors" />
                    </div>
                  </button>
                </StaggerItem>
              ))}
            </StaggerList>
          )}
        </div>

        {/* Current Workspace card */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-card flex flex-col">
          <div className="px-5 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-800">Current Workspace</h2>
          </div>
          {workspace ? (
            <div className="flex-1 px-5 py-4 flex flex-col gap-3">
              <div>
                <p className="text-base font-semibold text-slate-900">{workspace.name}</p>
                {workspace.description && (
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">{workspace.description}</p>
                )}
              </div>
              <div className="flex flex-wrap gap-2 text-xs text-slate-500">
                {workspace.financial_year && (
                  <span className="flex items-center gap-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-200">
                    <CalendarDays className="w-3 h-3" />
                    FY {workspace.financial_year}
                  </span>
                )}
                {workspace.assessment_year && (
                  <span className="bg-slate-50 px-2 py-1 rounded-lg border border-slate-200">
                    AY {workspace.assessment_year}
                  </span>
                )}
              </div>
              {workspace.status && <StatusBadge status={workspace.status} />}
              <div className="mt-auto pt-2">
                <button
                  onClick={() => navigate(`/workspaces/${currentWorkspaceId}`)}
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors cursor-pointer"
                >
                  Open workspace
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex-1 px-5 py-8 flex flex-col items-center justify-center text-center">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mb-3">
                <FolderOpen className="w-6 h-6 text-slate-400" />
              </div>
              <p className="text-sm font-semibold text-slate-700 mb-1">No workspace selected</p>
              <p className="text-xs text-slate-500 mb-4">Select a client to open a workspace.</p>
              <button
                onClick={() => navigate('/clients')}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer"
              >
                Get started
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      {currentWorkspaceId && (
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">Quick Actions</h2>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => navigate(`/workspaces/${currentWorkspaceId}/documents`)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-slate-300 hover:shadow-card transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
            >
              <FileText className="w-4 h-4 text-slate-500" />
              View Documents
            </button>
            <button
              onClick={() => navigate(`/workspaces/${currentWorkspaceId}/risks`)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-slate-300 hover:shadow-card transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
            >
              <ShieldAlert className="w-4 h-4 text-slate-500" />
              Risk Findings
            </button>
            <button
              onClick={() => navigate(`/workspaces/${currentWorkspaceId}/agent`)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-xl hover:bg-blue-100 hover:border-blue-300 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
            >
              <Bot className="w-4 h-4 text-blue-600" />
              Ask AI Agent
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
