import { useRef } from 'react'
import { motion, useMotionValue, useSpring, useReducedMotion } from 'motion/react'
import {
  FileText,
  Briefcase,
  ShieldAlert,
  BookOpen,
  Bot,
  LayoutDashboard,
  Building2,
} from 'lucide-react'
import { cn } from '../../lib/utils'

// ─── Types ────────────────────────────────────────────────────────────────────

interface NavEntry {
  icon: React.FC<React.SVGProps<SVGSVGElement>>
  label: string
  active: boolean
}

// ─── Static nav data ─────────────────────────────────────────────────────────

const TOP_NAV: NavEntry[] = [
  { icon: LayoutDashboard, label: 'Dashboard', active: false },
  { icon: Building2, label: 'Clients', active: false },
]

const WORKSPACE_NAV: NavEntry[] = [
  { icon: FileText, label: 'Documents', active: false },
  { icon: Briefcase, label: 'Processing', active: false },
  { icon: ShieldAlert, label: 'Risks', active: true },
  { icon: BookOpen, label: 'Knowledge', active: false },
  { icon: Bot, label: 'AI Agent', active: false },
]

// ─── Sub-components ───────────────────────────────────────────────────────────

function MockStatCard({
  label,
  value,
  valueColor,
}: {
  label: string
  value: string
  valueColor: string
}) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm">
      <p className={cn('text-lg font-bold tabular-nums leading-tight', valueColor)}>{value}</p>
      <p className="text-[10px] text-slate-500 mt-0.5 leading-tight">{label}</p>
    </div>
  )
}

function MockNavItem({ icon: Icon, label, active }: NavEntry) {
  return (
    <div
      className={cn(
        'relative flex items-center gap-2 px-2 py-1.5 rounded text-[11px] mx-0.5',
        active ? 'bg-blue-900/40 text-blue-300' : 'text-slate-500',
      )}
    >
      {active && (
        <span className="absolute left-0 top-[5px] bottom-[5px] w-0.5 bg-blue-500 rounded-r" />
      )}
      <Icon className="w-3 h-3 flex-shrink-0" />
      <span className="truncate">{label}</span>
    </div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function HeroDashboardMock() {
  const prefersReduced = useReducedMotion()
  const ref = useRef<HTMLDivElement>(null)

  const rotateXVal = useMotionValue(0)
  const rotateYVal = useMotionValue(0)
  const rotateX = useSpring(rotateXVal, { stiffness: 120, damping: 28 })
  const rotateY = useSpring(rotateYVal, { stiffness: 120, damping: 28 })

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (prefersReduced || !ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2
    rotateXVal.set(-y * 5)
    rotateYVal.set(x * 5)
  }

  const handleMouseLeave = () => {
    rotateXVal.set(0)
    rotateYVal.set(0)
  }

  return (
    /* aria-hidden: this is a decorative product preview — not interactive */
    <div
      ref={ref}
      style={{ perspective: 1200 }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="w-full max-w-[900px] mx-auto"
      aria-hidden="true"
    >
      <motion.div
        style={
          prefersReduced
            ? {
                boxShadow:
                  '0 40px 100px -20px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.06)',
              }
            : {
                rotateX,
                rotateY,
                transformStyle: 'preserve-3d',
                boxShadow:
                  '0 40px 100px -20px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.06)',
              }
        }
        className="rounded-2xl overflow-hidden"
      >
        <div className="flex h-[480px]">
          {/* ── Dark sidebar ── */}
          <div className="w-[148px] bg-[#0F172A] flex-shrink-0 flex flex-col py-2.5">
            {/* Brand */}
            <div className="flex items-center gap-2 px-3 pb-2.5 mb-1 border-b border-slate-800">
              <img src="/app-icon.png" alt="AuditPilot" className="w-5 h-5 rounded object-contain flex-shrink-0" />
              <span className="text-[11px] font-bold text-white truncate">AuditPilot</span>
            </div>

            {/* Top nav */}
            <nav className="space-y-0.5 pt-1">
              {TOP_NAV.map((item) => (
                <MockNavItem key={item.label} {...item} />
              ))}
            </nav>

            {/* Divider */}
            <div className="mx-3 my-2 border-t border-slate-800/60" />

            {/* Workspace section */}
            <div className="px-3 mb-1.5">
              <p className="text-[9px] font-semibold text-slate-600 uppercase tracking-widest">
                Workspace
              </p>
            </div>
            <nav className="space-y-0.5">
              {WORKSPACE_NAV.map((item) => (
                <MockNavItem key={item.label} {...item} />
              ))}
            </nav>
          </div>

          {/* ── Light content area ── */}
          <div className="flex-1 bg-[#F8FAFC] flex flex-col overflow-hidden min-w-0">
            {/* Topbar */}
            <div className="h-10 bg-white border-b border-slate-200 flex items-center px-3 gap-2 flex-shrink-0">
              <div className="flex items-center gap-1.5 flex-1 min-w-0">
                <span className="text-[10px] text-slate-400">AY 2024-25</span>
                <span className="text-slate-200">·</span>
                <span className="text-[11px] font-semibold text-slate-700 truncate">ACME Corp</span>
              </div>
              <div className="ml-auto w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <span className="text-[9px] font-bold text-white">U</span>
              </div>
            </div>

            {/* Page content */}
            <div className="flex-1 p-3 overflow-hidden">
              <p className="text-[11px] font-semibold text-slate-800 mb-2.5">Risk Findings</p>

              {/* Stat cards grid */}
              <div className="grid grid-cols-2 gap-2 mb-3">
                <MockStatCard
                  label="Documents Uploaded"
                  value="24"
                  valueColor="text-blue-700"
                />
                <MockStatCard
                  label="Processing Jobs"
                  value="3"
                  valueColor="text-amber-700"
                />
                <MockStatCard
                  label="Risk Findings"
                  value="12"
                  valueColor="text-red-700"
                />
                <MockStatCard
                  label="Evidence Chunks"
                  value="1,847"
                  valueColor="text-teal-700"
                />
              </div>

              {/* AI Agent response panel */}
              <div className="bg-white rounded-lg border border-slate-200 p-2.5 shadow-sm">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <Bot className="w-3.5 h-3.5 text-violet-600 flex-shrink-0" />
                  <span className="text-[10px] font-semibold text-slate-700">AI Agent</span>
                  <span className="ml-auto text-[9px] px-1.5 py-0.5 bg-violet-50 text-violet-700 rounded-full font-medium">
                    Grounded
                  </span>
                </div>
                <p className="text-[10px] text-slate-600 leading-relaxed">
                  3 high-priority risks found. Evidence is linked to source records and citations.
                </p>
                <div className="flex gap-1.5 mt-1.5 flex-wrap">
                  <span className="text-[9px] px-1.5 py-0.5 bg-red-50 text-red-700 rounded border border-red-100 font-medium">
                    TDS Mismatch
                  </span>
                  <span className="text-[9px] px-1.5 py-0.5 bg-amber-50 text-amber-700 rounded border border-amber-100 font-medium">
                    Short Deposit
                  </span>
                  <span className="text-[9px] px-1.5 py-0.5 bg-teal-50 text-teal-700 rounded border border-teal-100 font-medium">
                    Evidence
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
