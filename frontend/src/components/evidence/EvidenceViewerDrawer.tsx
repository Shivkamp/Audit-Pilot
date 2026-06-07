import { X, FileSearch, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { LoadingSpinner } from '../common/LoadingState'
import { EvidenceCard } from './EvidenceCard'
import { SourceTraceDrawer } from './SourceTraceDrawer'
import { useSourceTrace } from '../../hooks/useAgentRetrieval'
import type { EvidenceViewerState } from '../../hooks/useAgentRetrieval'

interface EvidenceViewerDrawerProps {
  state: EvidenceViewerState
  onClose: () => void
  workspaceId: string
  title?: string
}

/**
 * Drawer that displays evidence results for a risk finding.
 * Pair with useEvidenceViewer() hook.
 * Internally manages its own SourceTraceDrawer for nested source tracing.
 */
export function EvidenceViewerDrawer({
  state,
  onClose,
  workspaceId,
  title = 'Evidence',
}: EvidenceViewerDrawerProps) {
  const { isOpen, evidence, isLoading, error } = state
  const sourceTrace = useSourceTrace(workspaceId)

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="fixed inset-0 bg-black/20 z-40"
              aria-hidden="true"
              onClick={onClose}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
              role="dialog"
              aria-modal="true"
              aria-label={title}
              className="fixed inset-y-0 right-0 w-full max-w-lg bg-white shadow-drawer z-50 flex flex-col"
            >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <FileSearch className="w-4 h-4 text-slate-500" />
            <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
            {!isLoading && evidence.length > 0 && (
              <span className="px-1.5 py-0.5 bg-blue-50 text-blue-600 text-xs rounded-full border border-blue-200">
                {evidence.length}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            aria-label="Close evidence viewer"
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-16">
              <LoadingSpinner className="w-7 h-7 border-slate-200 border-t-blue-700 mb-3" />
              <p className="text-sm text-slate-500">Loading evidence…</p>
            </div>
          )}

          {!isLoading && error && (
            <div className="flex items-start gap-2.5 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium mb-0.5">Failed to load evidence</p>
                <p className="text-xs text-red-600">{error}</p>
              </div>
            </div>
          )}

          {!isLoading && !error && evidence.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <FileSearch className="w-12 h-12 text-slate-300 mb-3" />
              <p className="text-sm font-semibold text-slate-500">No evidence found</p>
              <p className="text-xs text-slate-400 mt-1 max-w-xs">
                No supporting evidence chunks are indexed for this finding.
              </p>
            </div>
          )}

          {!isLoading && !error && evidence.length > 0 && (
            <>
              <p className="text-xs text-slate-400">
                {evidence.length} evidence item{evidence.length !== 1 ? 's' : ''} retrieved
              </p>
              {evidence.map((ev, i) => (
                <EvidenceCard
                  key={ev.chunk_id ?? i}
                  evidence={ev}
                  index={i}
                  onViewSourceTrace={
                    ev.metadata?.source_type && ev.metadata?.source_id
                      ? (type, id) => sourceTrace.open(type, id)
                      : undefined
                  }
                />
              ))}
            </>
          )}
        </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Nested source trace drawer */}
      <SourceTraceDrawer state={sourceTrace} onClose={sourceTrace.close} />
    </>
  )
}
