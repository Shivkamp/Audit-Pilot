import type { WorkspaceRole } from '../../types/workspaceMember'

export function canUploadDocuments(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor'
}

export function canDeleteDocuments(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin'
}

export function canRunRiskCheck(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor'
}

export function canUpdateRiskFinding(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor'
}

export function canConfigureRiskRules(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin'
}

export function canManageMembers(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin'
}

export function canRebuildKnowledgeIndex(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor'
}

export function canDeleteKnowledgeIndex(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin'
}

export function canUseAgent(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor' || role === 'viewer'
}

export function isAtLeastEditor(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor'
}

export function isAtLeastAdmin(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin'
}

export function canRetryJobs(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner' || role === 'admin' || role === 'editor'
}

export function isOwner(role: WorkspaceRole | null | undefined): boolean {
  return role === 'owner'
}
