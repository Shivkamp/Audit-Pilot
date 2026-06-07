/**
 * Module 6 tests
 * Tests type/API alignment, evidence normalization, and pagination fixes.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { normalizeEvidenceItem } from '@/lib/evidence/normalizeEvidence'
import { renderWithProviders } from './helpers/test-utils'
import type { AgentEvidenceItem, EvidenceResult, AgentEvidenceRequest, RiskEvidenceRequest } from '@/types/agent'

// ─── normalizeEvidenceItem ────────────────────────────────────────────────────

describe('normalizeEvidenceItem', () => {
  it('reads source_type from direct field (AgentEvidenceItem shape)', () => {
    const item: AgentEvidenceItem = {
      content: 'Test content',
      score: 0.9,
      source_type: 'vendor_ledger',
      source_id: 'rec-123',
      chunk_type: 'csv_row',
      facts: {},
      citation: {},
    }
    const norm = normalizeEvidenceItem(item as unknown as EvidenceResult)
    expect(norm.source_type).toBe('vendor_ledger')
    expect(norm.source_id).toBe('rec-123')
    expect(norm.content).toBe('Test content')
    expect(norm.score).toBe(0.9)
  })

  it('reads source_type from metadata fallback (finding-context shape)', () => {
    const item: EvidenceResult = {
      chunk_id: 'chunk-abc',
      content: 'Normalized record data',
      score: 0.75,
      metadata: {
        source_type: 'normalized_record',
        source_id: 'rec-456',
      },
    }
    const norm = normalizeEvidenceItem(item)
    expect(norm.source_type).toBe('normalized_record')
    expect(norm.source_id).toBe('rec-456')
  })

  it('reads source_type from citation fallback', () => {
    const item = {
      content: 'Citation evidence',
      score: 0.6,
      citation: {
        source_type: 'invoice',
        source_id: 'inv-789',
        chunk_id: 'chunk-789',
      },
    }
    const norm = normalizeEvidenceItem(item as unknown as EvidenceResult)
    expect(norm.source_type).toBe('invoice')
    expect(norm.source_id).toBe('inv-789')
    expect(norm.chunk_id).toBe('chunk-789')
  })

  it('returns null source_type gracefully when all sources missing', () => {
    const item: EvidenceResult = {
      content: 'Anonymous evidence',
      score: 0.5,
    }
    const norm = normalizeEvidenceItem(item)
    expect(norm.source_type).toBeNull()
    expect(norm.source_id).toBeNull()
  })

  it('uses safe defaults for score and content', () => {
    const norm = normalizeEvidenceItem({} as EvidenceResult)
    expect(norm.score).toBe(0)
    expect(norm.content).toBe('')
  })

  it('preserves direct source_type over metadata (direct field wins)', () => {
    const item = {
      content: 'Direct wins',
      score: 0.8,
      source_type: 'direct_source',
      metadata: { source_type: 'metadata_source' },
    }
    const norm = normalizeEvidenceItem(item as unknown as EvidenceResult)
    expect(norm.source_type).toBe('direct_source')
  })
})

// ─── EvidenceCard component ──────────────────────────────────────────────────

// Minimal render wrapper (no router/query needed for EvidenceCard)
import { EvidenceCard } from '@/components/evidence/EvidenceCard'

describe('EvidenceCard', () => {
  it('renders source_type from direct field', () => {
    const evidence: EvidenceResult = {
      content: 'Test',
      score: 0.85,
      source_type: 'vendor_ledger',
      source_id: 'rec-1',
    }
    render(<EvidenceCard evidence={evidence} />)
    expect(screen.getByText('vendor_ledger')).toBeInTheDocument()
  })

  it('renders source_type from metadata fallback', () => {
    const evidence: EvidenceResult = {
      content: 'Test',
      score: 0.85,
      metadata: { source_type: 'normalized_record', source_id: 'rec-2' },
    }
    render(<EvidenceCard evidence={evidence} />)
    expect(screen.getByText('normalized_record')).toBeInTheDocument()
  })

  it('renders "Unknown source" when source_type is missing', () => {
    const evidence: EvidenceResult = {
      content: 'No source info',
      score: 0.5,
    }
    render(<EvidenceCard evidence={evidence} />)
    expect(screen.getByText('Unknown source')).toBeInTheDocument()
  })

  it('does NOT render source trace button when source_type missing', () => {
    const onViewSourceTrace = vi.fn()
    const evidence: EvidenceResult = {
      content: 'No source',
      score: 0.5,
    }
    render(<EvidenceCard evidence={evidence} onViewSourceTrace={onViewSourceTrace} />)
    expect(screen.queryByRole('button', { name: /view source trace/i })).not.toBeInTheDocument()
  })

  it('renders source trace button when both source_type and source_id are present', () => {
    const onViewSourceTrace = vi.fn()
    const evidence: EvidenceResult = {
      content: 'With source',
      score: 0.9,
      source_type: 'document',
      source_id: 'doc-1',
    }
    render(<EvidenceCard evidence={evidence} onViewSourceTrace={onViewSourceTrace} />)
    const btn = screen.getByRole('button', { name: /view source trace/i })
    expect(btn).toBeInTheDocument()
    fireEvent.click(btn)
    expect(onViewSourceTrace).toHaveBeenCalledWith('document', 'doc-1')
  })
})

// ─── Pagination component ─────────────────────────────────────────────────────

import { Pagination } from '@/components/common/Pagination'

describe('Pagination', () => {
  it('calls onPageSizeChange when page size is changed', () => {
    const onPageChange = vi.fn()
    const onPageSizeChange = vi.fn()
    render(
      <Pagination
        page={1}
        pageSize={25}
        totalItems={100}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />,
    )
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: '50' } })

    expect(onPageSizeChange).toHaveBeenCalledWith(50)
  })

  it('does NOT internally call onPageChange when page size changes (consumer owns reset)', () => {
    const onPageChange = vi.fn()
    const onPageSizeChange = vi.fn()
    render(
      <Pagination
        page={2}
        pageSize={25}
        totalItems={100}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />,
    )
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: '50' } })

    // onPageChange should NOT be called by the component itself
    expect(onPageChange).not.toHaveBeenCalled()
  })

  it('shows correct showing text', () => {
    render(
      <Pagination
        page={2}
        pageSize={10}
        totalItems={35}
        onPageChange={vi.fn()}
        onPageSizeChange={vi.fn()}
      />,
    )
    expect(screen.getByText(/showing 11–20 of 35/i)).toBeInTheDocument()
  })
})

// ─── Type contract tests ──────────────────────────────────────────────────────

describe('API request type contracts', () => {
  it('AgentEvidenceRequest uses limit, not top_k', () => {
    // Compile-time check via object literal conformance
    const req: AgentEvidenceRequest = {
      query: 'TDS mismatch vendors',
      limit: 10,
      include_source_trace: true,
    }
    expect(req.limit).toBe(10)
    // @ts-expect-error — top_k must not exist on AgentEvidenceRequest
    expect(req.top_k).toBeUndefined()
  })

  it('RiskEvidenceRequest uses risk_type, not risk_finding_ids', () => {
    const req: RiskEvidenceRequest = {
      risk_type: 'missing_pan',
      query: 'vendor PAN',
      limit: 5,
    }
    expect(req.risk_type).toBe('missing_pan')
    // @ts-expect-error — risk_finding_ids must not exist on RiskEvidenceRequest
    expect(req.risk_finding_ids).toBeUndefined()
  })
})
