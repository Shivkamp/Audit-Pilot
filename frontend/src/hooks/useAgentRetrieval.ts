import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { agentRetrievalApi } from '../lib/api/agentRetrieval'
import type { EvidenceResult, RiskFindingContext } from '../types/agent'

export function useRiskFindingContext(workspaceId: string, riskFindingId: string | null) {
  return useQuery({
    queryKey: ['riskFindingContext', workspaceId, riskFindingId],
    queryFn: () => agentRetrievalApi.getRiskFindingContext(workspaceId, riskFindingId!),
    enabled: !!workspaceId && !!riskFindingId,
    staleTime: 60_000,
  })
}

export interface SourceTraceState {
  source: { type: string; id: string } | null
  data: unknown
  isLoading: boolean
  error: string | null
}

/**
 * Imperative hook for fetching and displaying a single source trace on demand.
 * Returns open/close handlers and current state. Designed for use with SourceTraceDrawer.
 */
export function useSourceTrace(workspaceId: string) {
  const [state, setState] = useState<SourceTraceState>({
    source: null,
    data: null,
    isLoading: false,
    error: null,
  })

  const open = useCallback(
    async (sourceType: string, sourceId: string) => {
      setState({ source: { type: sourceType, id: sourceId }, data: null, isLoading: true, error: null })
      try {
        const data = await agentRetrievalApi.getSourceTrace(workspaceId, sourceType, sourceId)
        setState((prev) => ({ ...prev, data, isLoading: false }))
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Failed to load source trace'
        setState((prev) => ({ ...prev, isLoading: false, error: msg }))
      }
    },
    [workspaceId],
  )

  const close = useCallback(() => {
    setState({ source: null, data: null, isLoading: false, error: null })
  }, [])

  return { ...state, open, close }
}

export interface EvidenceViewerState {
  isOpen: boolean
  evidence: EvidenceResult[]
  isLoading: boolean
  error: string | null
}

/**
 * Imperative hook for fetching risk finding context evidence on demand.
 */
export function useEvidenceViewer(workspaceId: string) {
  const [state, setState] = useState<EvidenceViewerState>({
    isOpen: false,
    evidence: [],
    isLoading: false,
    error: null,
  })

  const openForFinding = useCallback(
    async (riskFindingId: string) => {
      setState({ isOpen: true, evidence: [], isLoading: true, error: null })
      try {
        const ctx: RiskFindingContext = await agentRetrievalApi.getRiskFindingContext(workspaceId, riskFindingId)
        // Map related_normalized_records to EvidenceResult shape for display
        const evidence: EvidenceResult[] = (ctx.related_normalized_records ?? []).map((rec, i) => ({
          chunk_id: String(rec.id ?? `record-${i}`),
          content: rec.normalized_data
            ? JSON.stringify(rec.normalized_data, null, 2)
            : String(rec.record_category ?? 'Normalized record'),
          score: typeof rec.normalization_confidence === 'number' ? rec.normalization_confidence : 0,
          document_id: rec.document_id ? String(rec.document_id) : null,
          metadata: {
            source_type: 'normalized_record',
            source_id: String(rec.id ?? ''),
            record_category: rec.record_category,
            normalization_status: rec.normalization_status,
          },
        }))
        setState({ isOpen: true, evidence, isLoading: false, error: null })
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Failed to load evidence'
        setState({ isOpen: true, evidence: [], isLoading: false, error: msg })
      }
    },
    [workspaceId],
  )

  const close = useCallback(() => {
    setState({ isOpen: false, evidence: [], isLoading: false, error: null })
  }, [])

  return { ...state, openForFinding, close }
}
