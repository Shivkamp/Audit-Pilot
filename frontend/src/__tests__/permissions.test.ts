/**
 * Permission helper unit tests
 *
 * Run: npm test
 * Watch: npm run test:watch
 */

import { describe, it, expect } from 'vitest'
import {
  canUploadDocuments,
  canDeleteDocuments,
  canRetryJobs,
  canManageMembers,
} from '@/lib/auth/permissions'
import type { WorkspaceRole } from '@/types/workspaceMember'

describe('canUploadDocuments', () => {
  it('owner can upload', () => expect(canUploadDocuments('owner')).toBe(true))
  it('admin can upload', () => expect(canUploadDocuments('admin')).toBe(true))
  it('editor can upload', () => expect(canUploadDocuments('editor')).toBe(true))
  it('viewer cannot upload', () => expect(canUploadDocuments('viewer')).toBe(false))
  it('null role cannot upload', () => expect(canUploadDocuments(null)).toBe(false))
  it('undefined role cannot upload', () => expect(canUploadDocuments(undefined)).toBe(false))
})

describe('canDeleteDocuments', () => {
  it('owner can delete', () => expect(canDeleteDocuments('owner')).toBe(true))
  it('admin can delete', () => expect(canDeleteDocuments('admin')).toBe(true))
  it('editor cannot delete', () => expect(canDeleteDocuments('editor')).toBe(false))
  it('viewer cannot delete', () => expect(canDeleteDocuments('viewer')).toBe(false))
})

describe('canRetryJobs', () => {
  it('owner can retry', () => expect(canRetryJobs('owner')).toBe(true))
  it('admin can retry', () => expect(canRetryJobs('admin')).toBe(true))
  it('editor can retry', () => expect(canRetryJobs('editor')).toBe(true))
  it('viewer cannot retry', () => expect(canRetryJobs('viewer')).toBe(false))
  it('null cannot retry', () => expect(canRetryJobs(null)).toBe(false))
})

describe('canManageMembers', () => {
  it('owner can manage', () => expect(canManageMembers('owner')).toBe(true))
  it('admin can manage', () => expect(canManageMembers('admin')).toBe(true))
  it('editor cannot manage', () => expect(canManageMembers('editor')).toBe(false))
  it('viewer cannot manage', () => expect(canManageMembers('viewer')).toBe(false))
})

describe('viewer role gates all mutating actions', () => {
  const role: WorkspaceRole = 'viewer'
  it('cannot upload', () => expect(canUploadDocuments(role)).toBe(false))
  it('cannot delete', () => expect(canDeleteDocuments(role)).toBe(false))
  it('cannot retry jobs', () => expect(canRetryJobs(role)).toBe(false))
  it('cannot manage members', () => expect(canManageMembers(role)).toBe(false))
})
