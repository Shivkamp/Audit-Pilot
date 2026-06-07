import { X, GitBranch, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { LoadingSpinner } from '../common/LoadingState'
import type { SourceTraceState } from '../../hooks/useAgentRetrieval'

interface SourceTraceDrawerProps {
  state: SourceTraceState
  onClose: () => void
}

/**
 * Shared drawer for displaying source trace data.
 * Pair with useSourceTrace() hook.
 */
export function SourceTraceDrawer({ state, onClose }: SourceTraceDrawerProps) {
  const { source, data, isLoading, error } = state

  return (
    <AnimatePresence>
      {source && (
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
            aria-label="Source trace"
            className="fixed inset-y-0 right-0 w-full max-w-md bg-white shadow-drawer z-50 flex flex-col"
          >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <GitBranch className="w-4 h-4 text-slate-500" />
            <h2 className="text-sm font-semibold text-slate-900">Source Trace</h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close source trace"
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {/* Source metadata */}
          <div className="mb-4 bg-slate-50 rounded-lg p-3 space-y-1.5 text-xs">
            <div className="flex gap-2">
              <span className="text-slate-400 w-20 flex-shrink-0">Source Type</span>
              <span className="font-medium text-slate-700">{source.type}</span>
            </div>
            <div className="flex gap-2">
              <span className="text-slate-400 w-20 flex-shrink-0">Source ID</span>
              <span className="font-mono text-slate-700 break-all">{source.id}</span>
            </div>
          </div>

          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner className="w-6 h-6 border-slate-200 border-t-blue-700" />
            </div>
          )}

          {!isLoading && error && (
            <div className="flex items-start gap-2.5 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!isLoading && !error && data != null && (
            <div className="bg-slate-50 rounded-lg p-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Trace Data
              </p>
              <pre className="text-xs text-slate-700 overflow-auto whitespace-pre-wrap break-all leading-relaxed">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          )}

          {!isLoading && !error && data == null && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <GitBranch className="w-10 h-10 text-slate-300 mb-3" />
              <p className="text-sm font-medium text-slate-500">No trace data available</p>
              <p className="text-xs text-slate-400 mt-1">
                The source could not be traced for this item.
              </p>
            </div>
          )}
        </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
