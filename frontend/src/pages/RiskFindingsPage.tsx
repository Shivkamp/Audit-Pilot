import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'motion/react'
import {
  ShieldAlert,
  Play,
  RefreshCw,
  X,
  Bot,
  Filter,
  FileSearch,
  ChevronUp,
  ChevronDown as ChevronDownIcon,
  ChevronsUpDown,
} from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { SeverityBadge } from '../components/common/SeverityBadge'
import { Pagination } from '../components/common/Pagination'
import { EvidenceViewerDrawer } from '../components/evidence/EvidenceViewerDrawer'
import {
  useRiskFindings,
  useRiskSummary,
  useRunRiskCheck,
  useUpdateRiskFindingStatus,
} from '../hooks/useRiskFindings'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { useAuth } from '../hooks/useAuth'
import { useEvidenceViewer } from '../hooks/useAgentRetrieval'
import { canRunRiskCheck, canUpdateRiskFinding } from '../lib/auth/permissions'
import { formatDate } from '../lib/utils'
import type { RiskFinding, RiskSeverity, RiskFindingStatus } from '../types/risk'

// ─── Constants ───────────────────────────────────────────────────────────────

const SEVERITY_OPTIONS: Array<{ label: string; value: RiskSeverity | '' }> = [
  { label: 'All severities', value: '' },
  { label: 'Critical', value: 'critical' },
  { label: 'High', value: 'high' },
  { label: 'Medium', value: 'medium' },
  { label: 'Low', value: 'low' },
  { label: 'Info', value: 'info' },
]

const STATUS_OPTIONS: Array<{ label: string; value: RiskFindingStatus | '' }> = [
  { label: 'All statuses', value: '' },
  { label: 'Open', value: 'open' },
  { label: 'Reviewed', value: 'reviewed' },
  { label: 'Resolved', value: 'resolved' },
  { label: 'Dismissed', value: 'dismissed' },
]

const STATUS_COLORS: Record<RiskFindingStatus, string> = {
  open: 'bg-red-100 text-red-700',
  reviewed: 'bg-amber-100 text-amber-700',
  resolved: 'bg-green-100 text-green-700',
  dismissed: 'bg-slate-100 text-slate-500',
}

// Severity sort rank — lower number = lower severity (ascending = low first)
const SEVERITY_RANK: Record<RiskSeverity, number> = {
  info: 1,
  low: 2,
  medium: 3,
  high: 4,
  critical: 5,
}

const STATUS_RANK: Record<RiskFindingStatus, number> = {
  dismissed: 1,
  resolved: 2,
  reviewed: 3,
  open: 4,
}

// ─── Sorting ─────────────────────────────────────────────────────────────────

type SortField = 'severity' | 'risk_type' | 'status' | 'created_at' | 'title'
type SortDirection = 'asc' | 'desc'

function SortIcon({ field, sortBy, dir }: { field: SortField; sortBy: SortField | null; dir: SortDirection }) {
  if (sortBy !== field) return <ChevronsUpDown className="w-3 h-3 text-slate-400 ml-1 inline" />
  return dir === 'asc'
    ? <ChevronUp className="w-3 h-3 text-blue-600 ml-1 inline" />
    : <ChevronDownIcon className="w-3 h-3 text-blue-600 ml-1 inline" />
}

function sortFindings(
  findings: RiskFinding[],
  sortBy: SortField | null,
  sortDir: SortDirection,
): RiskFinding[] {
  if (!sortBy) return findings
  return [...findings].sort((a, b) => {
    let cmp = 0
    switch (sortBy) {
      case 'severity':
        cmp = (SEVERITY_RANK[a.severity] ?? 0) - (SEVERITY_RANK[b.severity] ?? 0)
        break
      case 'risk_type':
        cmp = a.risk_type.localeCompare(b.risk_type)
        break
      case 'status':
        cmp = (STATUS_RANK[a.status] ?? 0) - (STATUS_RANK[b.status] ?? 0)
        break
      case 'created_at':
        cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        break
      case 'title':
        cmp = a.title.localeCompare(b.title)
        break
    }
    return sortDir === 'asc' ? cmp : -cmp
  })
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export function RiskFindingsPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const navigate = useNavigate()
  const { currentWorkspaceRole } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)
  const role = derivedRole ?? currentWorkspaceRole

  const { data: summary } = useRiskSummary(workspaceId)
  const { data: findings, isLoading, error, refetch } = useRiskFindings(workspaceId)
  const runRiskCheck = useRunRiskCheck(workspaceId)
  const updateStatus = useUpdateRiskFindingStatus(workspaceId)
  const evidenceViewer = useEvidenceViewer(workspaceId)

  const [selectedFinding, setSelectedFinding] = useState<RiskFinding | null>(null)
  const [filterSeverity, setFilterSeverity] = useState<RiskSeverity | ''>('')
  const [filterStatus, setFilterStatus] = useState<RiskFindingStatus | ''>('')
  const [filterText, setFilterText] = useState('')

  // Sorting
  const [sortBy, setSortBy] = useState<SortField | null>('created_at')
  const [sortDir, setSortDir] = useState<SortDirection>('desc')

  // Pagination
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  const canRun = canRunRiskCheck(role)
  const canUpdate = canUpdateRiskFinding(role)

  const handleSortClick = (field: SortField) => {
    if (sortBy === field) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(field)
      setSortDir('asc')
    }
    setPage(1)
  }

  const handleFilterChange = (apply: () => void) => {
    apply()
    setPage(1)
  }

  // Filter → sort → paginate
  const filtered = (findings ?? []).filter((f) => {
    if (filterSeverity && f.severity !== filterSeverity) return false
    if (filterStatus && f.status !== filterStatus) return false
    if (filterText) {
      const q = filterText.toLowerCase()
      if (
        !f.title.toLowerCase().includes(q) &&
        !f.risk_type.toLowerCase().includes(q) &&
        !(f.description ?? '').toLowerCase().includes(q)
      )
        return false
    }
    return true
  })

  const sorted = sortFindings(filtered, sortBy, sortDir)
  const totalFiltered = sorted.length
  const paginated = sorted.slice((page - 1) * pageSize, page * pageSize)

  const handleStatusChange = (findingId: string, status: RiskFindingStatus) => {
    updateStatus.mutate({ findingId, data: { status } })
    if (selectedFinding?.id === findingId) {
      setSelectedFinding((prev) => (prev ? { ...prev, status } : null))
    }
  }

  // ─── Sort header helper ────────────────────────────────────────────────────
  const SortTh = ({
    field,
    children,
    className = '',
  }: {
    field: SortField
    children: React.ReactNode
    className?: string
  }) => (
    <th
      scope="col"
            className={`px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-700 select-none focus:outline-none focus:text-blue-700 ${className}`}
      tabIndex={0}
      onClick={() => handleSortClick(field)}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && handleSortClick(field)}
      aria-sort={sortBy === field ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}
    >
      {children}
      <SortIcon field={field} sortBy={sortBy} dir={sortDir} />
    </th>
  )

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title="Risk Findings"
        subtitle="TDS mismatches and compliance issues detected in your documents"
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={() => refetch()}
              className="p-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
              aria-label="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            {canRun ? (
              <button
                onClick={() => runRiskCheck.mutate()}
                disabled={runRiskCheck.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <Play className="w-4 h-4" />
                {runRiskCheck.isPending ? 'Running…' : 'Run Risk Check'}
              </button>
            ) : (
              role !== null && (
                <span className="text-xs text-slate-400 italic">Requires: owner / admin / editor</span>
              )
            )}
          </div>
        }
      />

      {/* Summary Cards */}
      {summary && (
        <motion.div
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6"
          initial="hidden"
          animate="visible"
          variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.06, when: 'beforeChildren' } } }}
        >
          {[
            { label: 'Total', value: summary.total, cls: 'text-slate-900 bg-white border-slate-200' },
            { label: 'Critical', value: summary.critical, cls: 'text-red-800 bg-red-50 border-red-200' },
            { label: 'High', value: summary.high, cls: 'text-red-600 bg-red-50 border-red-200' },
            { label: 'Medium', value: summary.medium, cls: 'text-amber-700 bg-amber-50 border-amber-200' },
            { label: 'Open', value: summary.open, cls: 'text-blue-700 bg-blue-50 border-blue-200' },
          ].map(({ label, value, cls }) => (
            <motion.div
              key={label}
              variants={{ hidden: { opacity: 0, y: 10 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } } }}
              className={`rounded-xl border p-4 shadow-card ${cls}`}
            >
              <p className="text-xs font-semibold uppercase tracking-wider opacity-60">{label}</p>
              <p className="text-2xl font-bold tabular-nums mt-1">{value}</p>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <div className="relative flex-1 min-w-[180px] max-w-xs">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={filterText}
            onChange={(e) => handleFilterChange(() => setFilterText(e.target.value))}
            placeholder="Search findings…"
            className="w-full pl-8 pr-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <select
          value={filterSeverity}
          onChange={(e) =>
            handleFilterChange(() => setFilterSeverity(e.target.value as RiskSeverity | ''))
          }
          className="px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          {SEVERITY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) =>
            handleFilterChange(() => setFilterStatus(e.target.value as RiskFindingStatus | ''))
          }
          className="px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        {(filterText || filterSeverity || filterStatus) && (
          <button
            onClick={() =>
              handleFilterChange(() => {
                setFilterText('')
                setFilterSeverity('')
                setFilterStatus('')
              })
            }
            className="px-3 py-2 text-sm text-slate-500 hover:text-slate-700 cursor-pointer"
          >
            Clear
          </button>
        )}
      </div>

      {isLoading && <LoadingState />}
      {!!error && <ErrorState error={error as Error} onRetry={() => refetch()} className="mb-4" />}

      {!isLoading && !error && (!findings || findings.length === 0) && (
        <EmptyState
          icon={<ShieldAlert className="w-12 h-12" />}
          title="No risk findings"
          body="Run a risk check on your documents to detect TDS mismatches and compliance issues."
          action={
            canRun ? (
              <button
                onClick={() => runRiskCheck.mutate()}
                disabled={runRiskCheck.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer disabled:opacity-60"
              >
                <Play className="w-4 h-4" />
                Run Risk Check
              </button>
            ) : undefined
          }
        />
      )}

      {!isLoading && findings && findings.length > 0 && filtered.length === 0 && (
        <EmptyState
          icon={<ShieldAlert className="w-12 h-12" />}
          title="No matching findings"
          body="Try adjusting your filters."
        />
      )}

      {!isLoading && paginated.length > 0 && (
        <>
          <div className="overflow-hidden border border-slate-200 rounded-xl bg-white shadow-card">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <SortTh field="severity">Severity</SortTh>
                  <SortTh field="title">Title</SortTh>
                  <SortTh field="risk_type" className="hidden md:table-cell">
                    Risk Type
                  </SortTh>
                  <SortTh field="status">Status</SortTh>
                  <SortTh field="created_at" className="hidden lg:table-cell">
                    Date
                  </SortTh>
                  <th
                    scope="col"
                    className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {paginated.map((finding) => (
                  <tr
                    key={finding.id}
                    className={`hover:bg-slate-50 transition-colors duration-100 cursor-pointer ${
                      {
                        critical: 'border-l-2 border-l-red-700',
                        high:     'border-l-2 border-l-red-400',
                        medium:   'border-l-2 border-l-amber-400',
                        low:      'border-l-2 border-l-green-500',
                        info:     'border-l-2 border-l-blue-400',
                      }[finding.severity] ?? ''
                    }`}
                    onClick={() => setSelectedFinding(finding)}
                  >
                    <td className="px-4 py-3">
                      <SeverityBadge severity={finding.severity} />
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-900 max-w-[200px] truncate">
                        {finding.title}
                      </p>
                      {finding.description && (
                        <p className="text-xs text-slate-500 mt-0.5 max-w-[200px] truncate">
                          {finding.description}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-600 hidden md:table-cell">
                      {finding.risk_type.replace(/_/g, ' ')}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[finding.status]}`}
                      >
                        {finding.status.charAt(0).toUpperCase() + finding.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500 hidden lg:table-cell">
                      {formatDate(finding.created_at)}
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-2">
                        {canUpdate && (
                          <select
                            value={finding.status}
                            onChange={(e) =>
                              handleStatusChange(finding.id, e.target.value as RiskFindingStatus)
                            }
                            disabled={updateStatus.isPending}
                            onClick={(e) => e.stopPropagation()}
                            className="text-xs border border-slate-200 rounded-lg px-2 py-1 text-slate-700 bg-white cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                          >
                            <option value="open">Open</option>
                            <option value="reviewed">Reviewed</option>
                            <option value="resolved">Resolved</option>
                            <option value="dismissed">Dismissed</option>
                          </select>
                        )}
                        <button
                          onClick={() => navigate(`/workspaces/${workspaceId}/agent`)}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer"
                          title="Ask AI about this finding"
                        >
                          <Bot className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            page={page}
            pageSize={pageSize}
            totalItems={totalFiltered}
            onPageChange={setPage}
            onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
          />
        </>
      )}

      {/* Finding detail drawer */}
      <AnimatePresence>
        {selectedFinding && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="fixed inset-0 bg-black/20 z-40"
              onClick={() => setSelectedFinding(null)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
              role="dialog"
              aria-modal="true"
              aria-label="Finding details"
              className="fixed inset-y-0 right-0 w-full max-w-md bg-white shadow-drawer z-50 flex flex-col"
            >
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
              <div className="flex items-center gap-2.5">
                <ShieldAlert className="w-4 h-4 text-slate-500" />
                <h2 className="text-sm font-semibold text-slate-900">Finding Details</h2>
              </div>
              <button
                onClick={() => setSelectedFinding(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
              <div>
                <h3 className="text-base font-semibold text-slate-900">{selectedFinding.title}</h3>
                <p className="text-xs font-mono text-slate-400 mt-0.5">
                  {selectedFinding.id.slice(0, 8)}…
                </p>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <SeverityBadge severity={selectedFinding.severity} />
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[selectedFinding.status]}`}
                >
                  {selectedFinding.status.charAt(0).toUpperCase() + selectedFinding.status.slice(1)}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="text-slate-400 font-medium mb-0.5">Risk Type</p>
                  <p className="text-slate-700">{selectedFinding.risk_type.replace(/_/g, ' ')}</p>
                </div>
                <div>
                  <p className="text-slate-400 font-medium mb-0.5">Date</p>
                  <p className="text-slate-700">{formatDate(selectedFinding.created_at)}</p>
                </div>
                {selectedFinding.document_id && (
                  <div className="col-span-2">
                    <p className="text-slate-400 font-medium mb-0.5">Document</p>
                    <p className="text-slate-700 font-mono">
                      {selectedFinding.document_id.slice(0, 16)}…
                    </p>
                  </div>
                )}
              </div>
              {selectedFinding.description && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Description
                  </p>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {selectedFinding.description}
                  </p>
                </div>
              )}
              {selectedFinding.risk_data && Object.keys(selectedFinding.risk_data).length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    Details
                  </p>
                  <div className="bg-slate-50 rounded-lg p-3 space-y-1.5">
                    {Object.entries(selectedFinding.risk_data).map(([k, v]) => (
                      <div key={k} className="grid grid-cols-[140px_1fr] gap-2 text-xs">
                        <span className="text-slate-500 font-medium">{k.replace(/_/g, ' ')}</span>
                        <span className="text-slate-800 break-all">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {selectedFinding.related_normalized_record_ids &&
                selectedFinding.related_normalized_record_ids.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                      Related Records
                    </p>
                    <div className="space-y-1">
                      {selectedFinding.related_normalized_record_ids.map((id) => (
                        <p key={id} className="text-xs text-slate-600 font-mono">
                          {id.slice(0, 16)}…
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              {canUpdate && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    Update Status
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(['open', 'reviewed', 'resolved', 'dismissed'] as RiskFindingStatus[]).map(
                      (s) => (
                        <button
                          key={s}
                          onClick={() => handleStatusChange(selectedFinding.id, s)}
                          disabled={updateStatus.isPending || selectedFinding.status === s}
                          className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${
                            selectedFinding.status === s
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                          }`}
                        >
                          {s.charAt(0).toUpperCase() + s.slice(1)}
                        </button>
                      ),
                    )}
                  </div>
                </div>
              )}
            </div>
            <div className="border-t border-slate-200 px-5 py-3 space-y-2">
              <button
                onClick={() => evidenceViewer.openForFinding(selectedFinding.id)}
                disabled={evidenceViewer.isLoading}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer disabled:opacity-60"
              >
                <FileSearch className="w-4 h-4" />
                {evidenceViewer.isLoading ? 'Loading evidence…' : 'View Evidence'}
              </button>
              <button
                onClick={() => navigate(`/workspaces/${workspaceId}/agent`)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-xl hover:bg-blue-100 transition-colors cursor-pointer"
              >
                <Bot className="w-4 h-4" />
                Ask AI about this finding
              </button>
            </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Evidence viewer drawer */}
      <EvidenceViewerDrawer
        state={evidenceViewer}
        onClose={evidenceViewer.close}
        workspaceId={workspaceId}
        title="Finding Evidence"
      />
    </div>
  )
}
