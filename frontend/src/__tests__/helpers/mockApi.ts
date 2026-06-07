import type { RiskFinding, RiskSeverity, RiskFindingStatus } from '@/types/risk'
import type { RiskRuleConfig } from '@/types/riskRule'
import type { KnowledgeChunk } from '@/types/knowledge'
import type { EvidenceResult } from '@/types/agent'

export function mockRiskFinding(overrides: Partial<RiskFinding> = {}): RiskFinding {
  return {
    id: 'finding-1',
    workspace_id: 'ws-1',
    risk_type: 'tds_short_deduction',
    severity: 'high' as RiskSeverity,
    title: 'TDS Short Deduction',
    status: 'open' as RiskFindingStatus,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides,
  }
}

export function mockRiskRuleConfig(overrides: Partial<RiskRuleConfig> = {}): RiskRuleConfig {
  return {
    id: 'rule-1',
    workspace_id: 'ws-1',
    rule_key: 'tds_short_deduction',
    risk_type: 'tds_short_deduction',
    is_enabled: true,
    severity: 'high' as RiskSeverity,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides,
  }
}

export function mockKnowledgeChunk(overrides: Partial<KnowledgeChunk> = {}): KnowledgeChunk {
  return {
    id: 'chunk-1',
    workspace_id: 'ws-1',
    source_type: 'document',
    source_id: 'doc-1',
    chunk_type: 'text',
    chunk_text: 'Sample chunk text content.',
    embedding_status: 'embedded',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides,
  }
}

export function mockEvidenceResult(overrides: Partial<EvidenceResult> = {}): EvidenceResult {
  return {
    chunk_id: 'chunk-1',
    score: 0.87,
    source_type: 'document',
    source_id: 'doc-1',
    document_id: 'doc-1',
    content: 'Sample evidence content.',
    chunk_type: 'text',
    ...overrides,
  }
}
