/**
 * Module 5 integration tests
 * Tests bulk save, sorting/pagination, inline errors, evidence viewer, and 403 handling.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from './helpers/test-utils'
import { mockRiskFinding, mockRiskRuleConfig } from './helpers/mockApi'
import type { EvidenceResult } from '@/types/agent'

// ─── Mock factories ───────────────────────────────────────────────────────────

export function mockEvidenceResult(overrides: Partial<EvidenceResult> = {}): EvidenceResult {
  return {
    chunk_id: 'chunk-1',
    score: 0.87,
    source_type: 'document',
    source_id: 'doc-1',
    document_id: 'doc-1',
    content: 'Sample evidence content for testing.',
    chunk_type: 'text',
    ...overrides,
  }
}

// ─── Mock hooks ───────────────────────────────────────────────────────────────

vi.mock('@/hooks/useRiskFindings', () => ({
  useRiskFindings: vi.fn(() => ({ data: [], isLoading: false, error: null, refetch: vi.fn() })),
  useRiskSummary: vi.fn(() => ({ data: null })),
  useRunRiskCheck: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useUpdateRiskFindingStatus: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}))

vi.mock('@/hooks/useRiskRules', () => ({
  useRiskRules: vi.fn(() => ({ data: [], isLoading: false, error: null, refetch: vi.fn() })),
  useInitializeRiskRules: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useResetRiskRuleDefaults: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useUpdateRiskRule: vi.fn(() => ({ mutate: vi.fn(), isPending: false, isSuccess: false })),
  useBulkUpdateRiskRules: vi.fn(() => ({ mutate: vi.fn(), isPending: false, isError: false })),
}))

vi.mock('@/hooks/useMyWorkspaceRole', () => ({
  useMyWorkspaceRole: vi.fn(() => ({ role: 'owner', isLoading: false })),
}))

vi.mock('@/hooks/useAgentChat', () => ({
  useAgentChat: vi.fn(() => ({
    messages: [],
    lastResponse: null,
    sendMessage: vi.fn(),
    retryMessage: vi.fn(),
    clearMessages: vi.fn(),
    isLoading: false,
    includeEvidence: false,
    setIncludeEvidence: vi.fn(),
    includeSourceTrace: false,
    setIncludeSourceTrace: vi.fn(),
  })),
}))

vi.mock('@/hooks/useAgentRetrieval', () => ({
  useEvidenceViewer: vi.fn(() => ({
    isOpen: false,
    evidence: undefined,
    isLoading: false,
    error: null,
    openForFinding: vi.fn(),
    close: vi.fn(),
  })),
  useSourceTrace: vi.fn(() => ({
    source: null,
    data: null,
    isLoading: false,
    error: null,
    open: vi.fn(),
    close: vi.fn(),
  })),
  useRiskFindingContext: vi.fn(() => ({ data: undefined, isLoading: false })),
}))

// ─── Lazy page imports (after mocks) ──────────────────────────────────────────

// Import mocked hooks for per-test overrides (vi.mock hoists, so these get the mocked versions)
import { useMyWorkspaceRole } from '@/hooks/useMyWorkspaceRole'
import { useRiskFindings } from '@/hooks/useRiskFindings'
import { useRiskRules, useBulkUpdateRiskRules } from '@/hooks/useRiskRules'
import { useAgentChat } from '@/hooks/useAgentChat'
import { useEvidenceViewer, useSourceTrace } from '@/hooks/useAgentRetrieval'

const { RiskFindingsPage } = await import('@/pages/RiskFindingsPage')
const { RiskRuleSettingsPage } = await import('@/pages/RiskRuleSettingsPage')
const { AgentChatPage } = await import('@/pages/AgentChatPage')

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('Module 5 — Polish + Evidence UX', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset all mocks to their default state
    vi.mocked(useMyWorkspaceRole).mockReturnValue({ role: 'owner', isLoading: false })
    vi.mocked(useBulkUpdateRiskRules).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
    } as unknown as ReturnType<typeof useBulkUpdateRiskRules>)
    vi.mocked(useEvidenceViewer).mockReturnValue({
      isOpen: false,
      evidence: [],
      isLoading: false,
      error: null,
      openForFinding: vi.fn(),
      close: vi.fn(),
    })
    vi.mocked(useAgentChat).mockReturnValue({
      messages: [],
      lastResponse: null,
      sendMessage: vi.fn(),
      retryMessage: vi.fn(),
      clearMessages: vi.fn(),
      isLoading: false,
      includeEvidence: false,
      setIncludeEvidence: vi.fn(),
      includeSourceTrace: false,
      setIncludeSourceTrace: vi.fn(),
    } as unknown as ReturnType<typeof useAgentChat>)
  })

  // ─── RiskRuleSettingsPage ─────────────────────────────────────────────────

  describe('RiskRuleSettingsPage — bulk save', () => {
    it('does not show "Save All Changes" when no rows are dirty', () => {
      vi.mocked(useRiskRules).mockReturnValue({
        data: [mockRiskRuleConfig({ rule_key: 'tds_short_deduction' })],
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as ReturnType<typeof useRiskRules>)

      renderWithProviders(<RiskRuleSettingsPage />, {
        initialRoute: '/workspaces/ws-1/risk-rules',
      })

      expect(screen.queryByText(/Save All Changes/i)).not.toBeInTheDocument()
    })

    it('viewer role: shows read-only notice, no save buttons', () => {
      vi.mocked(useMyWorkspaceRole).mockReturnValue({ role: 'viewer', isLoading: false })
      vi.mocked(useRiskRules).mockReturnValue({
        data: [mockRiskRuleConfig()],
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as ReturnType<typeof useRiskRules>)

      renderWithProviders(<RiskRuleSettingsPage />, {
        initialRoute: '/workspaces/ws-1/risk-rules',
        auth: { currentWorkspaceRole: 'viewer' },
      })

      expect(screen.getByText(/read-only/i)).toBeInTheDocument()
      expect(screen.queryByText(/Save All Changes/i)).not.toBeInTheDocument()
    })
  })

  // ─── RiskFindingsPage ────────────────────────────────────────────────────

  describe('RiskFindingsPage — sorting + pagination', () => {
    const findings = [
      mockRiskFinding({ id: 'f1', severity: 'low', title: 'Alpha Finding', created_at: '2024-01-01T00:00:00Z' }),
      mockRiskFinding({ id: 'f2', severity: 'critical', title: 'Beta Finding', created_at: '2024-02-01T00:00:00Z' }),
      mockRiskFinding({ id: 'f3', severity: 'medium', title: 'Gamma Finding', created_at: '2024-03-01T00:00:00Z' }),
    ]

    beforeEach(() => {
      vi.mocked(useRiskFindings).mockReturnValue({
        data: findings,
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as ReturnType<typeof useRiskFindings>)
    })

    it('renders all findings in default sort (created_at desc)', () => {
      renderWithProviders(<RiskFindingsPage />, {
        initialRoute: '/workspaces/ws-1/risks',
      })

      const rows = screen.getAllByRole('row')
      // First data row should be newest (Gamma), last is oldest (Alpha)
      expect(rows[1]).toHaveTextContent('Gamma Finding')
      expect(rows[3]).toHaveTextContent('Alpha Finding')
    })

    it('clicking Severity header sorts by severity ascending', async () => {
      renderWithProviders(<RiskFindingsPage />, {
        initialRoute: '/workspaces/ws-1/risks',
      })

      fireEvent.click(screen.getByRole('columnheader', { name: /severity/i }))

      await waitFor(() => {
        const rows = screen.getAllByRole('row')
        // Ascending severity: low first, then medium, then critical
        expect(rows[1]).toHaveTextContent('Alpha Finding')
        expect(rows[3]).toHaveTextContent('Beta Finding')
      })
    })

    it('pagination shows page size selector', () => {
      renderWithProviders(<RiskFindingsPage />, {
        initialRoute: '/workspaces/ws-1/risks',
      })

      // The Pagination component shows a page size select
      expect(screen.getByText(/showing/i)).toBeInTheDocument()
    })
  })

  // ─── RiskFindingsPage — evidence viewer ──────────────────────────────────

  describe('RiskFindingsPage — evidence viewer', () => {
    it('View Evidence button calls openForFinding when finding drawer is open', async () => {
      const openForFinding = vi.fn()
      vi.mocked(useEvidenceViewer).mockReturnValue({
        isOpen: false,
        evidence: [],
        isLoading: false,
        error: null,
        openForFinding,
        close: vi.fn(),
      })
      vi.mocked(useRiskFindings).mockReturnValue({
        data: [mockRiskFinding({ id: 'f1', title: 'Test Finding' })],
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as ReturnType<typeof useRiskFindings>)

      renderWithProviders(<RiskFindingsPage />, {
        initialRoute: '/workspaces/ws-1/risks',
      })

      // Open finding detail drawer by clicking row
      fireEvent.click(screen.getByText('Test Finding'))

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByRole('button', { name: /view evidence/i }))
      expect(openForFinding).toHaveBeenCalledWith('f1')
    })
  })

  // ─── AgentChatPage — inline errors + retry ───────────────────────────────

  describe('AgentChatPage — inline error messages', () => {
    it('renders error message with red styling when message has _error flag', () => {
      const retryMessage = vi.fn()
      vi.mocked(useAgentChat).mockReturnValue({
        messages: [
          { role: 'user', content: 'What are the risks?' },
          {
            role: 'assistant',
            content: 'The agent could not answer right now. Please try again.',
            _error: true,
            _retryContent: 'What are the risks?',
          },
        ],
        lastResponse: null,
        sendMessage: vi.fn(),
        retryMessage,
        clearMessages: vi.fn(),
        isLoading: false,
        includeEvidence: false,
        setIncludeEvidence: vi.fn(),
        includeSourceTrace: false,
        setIncludeSourceTrace: vi.fn(),
      } as unknown as ReturnType<typeof useAgentChat>)

      renderWithProviders(<AgentChatPage />, {
        initialRoute: '/workspaces/ws-1/agent',
      })

      expect(screen.getByText('The agent could not answer right now. Please try again.')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
    })

    it('clicking Retry calls retryMessage with original content', async () => {
      const retryMessage = vi.fn()
      vi.mocked(useAgentChat).mockReturnValue({
        messages: [
          { role: 'user', content: 'Test question' },
          {
            role: 'assistant',
            content: 'Error occurred.',
            _error: true,
            _retryContent: 'Test question',
          },
        ],
        lastResponse: null,
        sendMessage: vi.fn(),
        retryMessage,
        clearMessages: vi.fn(),
        isLoading: false,
        includeEvidence: false,
        setIncludeEvidence: vi.fn(),
        includeSourceTrace: false,
        setIncludeSourceTrace: vi.fn(),
      } as unknown as ReturnType<typeof useAgentChat>)

      renderWithProviders(<AgentChatPage />, {
        initialRoute: '/workspaces/ws-1/agent',
      })

      fireEvent.click(screen.getByRole('button', { name: /retry/i }))
      expect(retryMessage).toHaveBeenCalledWith('Test question')
    })

    it('403 error message does not show Retry button (no _retryContent)', () => {
      vi.mocked(useAgentChat).mockReturnValue({
        messages: [
          {
            role: 'assistant',
            content: 'You do not have permission to use the agent for this workspace.',
            _error: true,
            // no _retryContent — 403 should not be retried
          },
        ],
        lastResponse: null,
        sendMessage: vi.fn(),
        retryMessage: vi.fn(),
        clearMessages: vi.fn(),
        isLoading: false,
        includeEvidence: false,
        setIncludeEvidence: vi.fn(),
        includeSourceTrace: false,
        setIncludeSourceTrace: vi.fn(),
      } as unknown as ReturnType<typeof useAgentChat>)

      renderWithProviders(<AgentChatPage />, {
        initialRoute: '/workspaces/ws-1/agent',
      })

      expect(screen.getByText(/You do not have permission/i)).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument()
    })
  })

  // ─── EvidenceViewerDrawer rendered state ──────────────────────────────────

  describe('EvidenceViewerDrawer — visible state', () => {
    it('shows evidence items when drawer is open with evidence data', async () => {
      // Import component directly (not via page wrapper) to test the drawer standalone
      const { EvidenceViewerDrawer } = await import('@/components/evidence/EvidenceViewerDrawer')

      const evidence = [
        mockEvidenceResult({ chunk_id: 'c1', content: 'Invoice #INV-001 from TechCorp' }),
        mockEvidenceResult({ chunk_id: 'c2', content: 'TDS challan reference CH-2024' }),
      ]

      const state = {
        isOpen: true,
        evidence,
        isLoading: false,
        error: null,
        openForFinding: vi.fn(),
        close: vi.fn(),
      }

      vi.mocked(useSourceTrace).mockReturnValue({
        source: null,
        data: null,
        isLoading: false,
        error: null,
        open: vi.fn(),
        close: vi.fn(),
      })

      renderWithProviders(
        <EvidenceViewerDrawer
          state={state}
          onClose={state.close}
          workspaceId="ws-1"
          title="Test Evidence"
        />,
      )

      await waitFor(() => {
        expect(screen.getByText('Invoice #INV-001 from TechCorp')).toBeInTheDocument()
        expect(screen.getByText('TDS challan reference CH-2024')).toBeInTheDocument()
      })
    })
  })
})
