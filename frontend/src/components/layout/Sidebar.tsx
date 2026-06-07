import { Link, useLocation, useParams } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  FolderOpen,
  FileText,
  Briefcase,
  ShieldAlert,
  BookOpen,
  Bot,
  Users,
  Settings,
} from 'lucide-react'
import { motion } from 'motion/react'
import { cn } from '../../lib/utils'
import { useAuth } from '../../hooks/useAuth'

interface NavItem {
  label: string
  icon: React.FC<React.SVGProps<SVGSVGElement>>
  href: string
  workspaceScoped?: boolean
}

const TOP_NAV: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
  { label: 'Clients', icon: Building2, href: '/clients' },
]

interface NavLinkProps {
  label: string
  icon: React.FC<React.SVGProps<SVGSVGElement>>
  href: string
  isActive: boolean
}

function NavLink({ label, icon: Icon, href, isActive }: NavLinkProps) {
  return (
    <Link
      to={href}
      className={cn(
        'relative flex items-center gap-3 px-3 py-2 mx-1 rounded-lg text-sm font-medium transition-colors duration-150 cursor-pointer group',
        isActive
          ? 'bg-blue-900/40 text-blue-300'
          : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200',
      )}
      aria-current={isActive ? 'page' : undefined}
    >
      {/* Active indicator bar */}
      {isActive && (
        <motion.span
          layoutId="sidebar-active-indicator"
          className="absolute left-0 top-1/4 bottom-1/4 w-0.5 bg-blue-500 rounded-r-full"
          transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
        />
      )}
      <Icon
        className={cn(
          'w-4 h-4 flex-shrink-0 transition-colors duration-150',
          isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300',
        )}
      />
      <span>{label}</span>
    </Link>
  )
}

function WorkspaceNav({ workspaceId }: { workspaceId: string }) {
  const location = useLocation()

  const items: NavItem[] = [
    { label: 'Workspace', icon: FolderOpen, href: `/workspaces/${workspaceId}` },
    { label: 'Documents', icon: FileText, href: `/workspaces/${workspaceId}/documents` },
    { label: 'Processing Jobs', icon: Briefcase, href: `/workspaces/${workspaceId}/jobs` },
    { label: 'Risk Findings', icon: ShieldAlert, href: `/workspaces/${workspaceId}/risks` },
    { label: 'Knowledge Search', icon: BookOpen, href: `/workspaces/${workspaceId}/knowledge` },
    { label: 'AI Agent', icon: Bot, href: `/workspaces/${workspaceId}/agent` },
    { label: 'Members', icon: Users, href: `/workspaces/${workspaceId}/members` },
  ]

  return (
    <>
      <div className="px-4 pt-4 pb-1">
        <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest">
          Workspace
        </p>
      </div>
      <nav className="space-y-0.5">
        {items.map(({ label, icon, href }) => (
          <NavLink
            key={href}
            label={label}
            icon={icon}
            href={href}
            isActive={location.pathname === href}
          />
        ))}
      </nav>
    </>
  )
}

export function Sidebar() {
  const location = useLocation()
  const { workspaceId: urlWorkspaceId } = useParams<{ workspaceId?: string }>()
  const { currentWorkspaceId } = useAuth()
  const workspaceId = urlWorkspaceId ?? currentWorkspaceId ?? undefined

  return (
    <aside className="flex flex-col w-60 min-h-screen bg-gradient-to-b from-[#0f1e38] via-[#0f172a] to-[#0b1220] border-r border-slate-800/60 flex-shrink-0">
      {/* Brand */}
      <div className="h-14 flex items-center gap-2.5 px-4 border-b border-slate-800/60 flex-shrink-0">
        <img src="/app-icon.png" alt="AuditPilot" className="w-7 h-7 rounded-lg object-contain flex-shrink-0" />
        <span className="text-[15px] font-bold text-white tracking-tight">AuditPilot</span>
      </div>

      {/* Top nav */}
      <nav className="pt-3 space-y-0.5">
        {TOP_NAV.map(({ label, icon, href }) => (
          <NavLink
            key={href}
            label={label}
            icon={icon}
            href={href}
            isActive={location.pathname === href}
          />
        ))}
      </nav>

      {/* Divider */}
      <div className="mx-4 my-3 border-t border-slate-800/60" />

      {/* Workspace-scoped nav */}
      {workspaceId ? (
        <WorkspaceNav workspaceId={workspaceId} />
      ) : (
        <div className="px-4 py-3">
          <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest mb-2">
            Workspace
          </p>
          <p className="text-xs text-slate-600 leading-relaxed">
            Select a workspace to see workspace navigation.
          </p>
        </div>
      )}

      {/* Bottom */}
      <div className="mt-auto border-t border-slate-800/60 py-2">
        <NavLink
          label="Settings"
          icon={Settings}
          href={workspaceId ? `/workspaces/${workspaceId}/settings` : '/dashboard'}
          isActive={location.pathname.endsWith('/settings')}
        />
      </div>
    </aside>
  )
}
