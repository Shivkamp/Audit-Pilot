import { GitBranch } from 'lucide-react'
import { cn } from '../../lib/utils'
import { normalizeEvidenceItem } from '../../lib/evidence/normalizeEvidence'
import type { EvidenceResult } from '../../types/agent'

interface EvidenceCardProps {
  evidence: EvidenceResult
  index?: number
  onViewSourceTrace?: (sourceType: string, sourceId: string) => void
  className?: string
}

/**
 * Displays a single evidence result with score, text, and source trace trigger.
 * Internally normalizes the evidence item to handle multiple backend response shapes.
 */
export function EvidenceCard({ evidence, index, onViewSourceTrace, className }: EvidenceCardProps) {
  const norm = normalizeEvidenceItem(evidence)
  const scorePercent = norm.score != null ? (norm.score * 100).toFixed(1) : null
  const canSourceTrace = !!(onViewSourceTrace && norm.source_type && norm.source_id)

  return (
    <div className={cn('bg-white border border-slate-200 rounded-xl p-4 shadow-card', className)}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {index != null && (
            <span className="text-xs text-slate-400 font-medium">#{index + 1}</span>
          )}
          <span className="px-1.5 py-0.5 bg-blue-50 text-blue-600 text-xs rounded border border-blue-200">
            {norm.source_type ?? 'Unknown source'}
          </span>
          {norm.document_id && (
            <span className="text-xs text-slate-400 font-mono">
              doc: {norm.document_id.slice(0, 12)}…
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {scorePercent && (
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
              {scorePercent}%
            </span>
          )}
          {canSourceTrace && (
            <button
              onClick={() => onViewSourceTrace!(norm.source_type!, norm.source_id!)}
              aria-label="View source trace"
              className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <GitBranch className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Evidence content */}
      <p className="text-sm text-slate-700 leading-relaxed">
        {norm.content || <span className="text-slate-400 italic">No content</span>}
      </p>

      {/* Chunk ID */}
      {norm.chunk_id && (
        <p className="text-xs text-slate-400 mt-2 font-mono">
          chunk: {norm.chunk_id.slice(0, 20)}…
        </p>
      )}
    </div>
  )
}
