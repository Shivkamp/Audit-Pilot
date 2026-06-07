/**
 * Job status helper tests
 *
 * Tests that active/terminal status detection is correct for polling.
 */

import { describe, it, expect } from 'vitest'
import { isActiveJobStatus, ACTIVE_JOB_STATUSES, TERMINAL_JOB_STATUSES } from '@/types/job'

describe('isActiveJobStatus', () => {
  it.each(ACTIVE_JOB_STATUSES)('"%s" is active', (status) => {
    expect(isActiveJobStatus(status)).toBe(true)
  })

  it.each(TERMINAL_JOB_STATUSES)('"%s" is NOT active (terminal)', (status) => {
    expect(isActiveJobStatus(status)).toBe(false)
  })

  it('unknown status is not active', () => {
    expect(isActiveJobStatus('cancelled')).toBe(false)
    expect(isActiveJobStatus('')).toBe(false)
    expect(isActiveJobStatus('unknown')).toBe(false)
  })
})

describe('polling logic simulation', () => {
  it('stops polling when all jobs are terminal', () => {
    const jobs = [
      { id: '1', status: 'completed' },
      { id: '2', status: 'failed' },
    ]
    const hasActive = jobs.some((j) => isActiveJobStatus(j.status))
    expect(hasActive).toBe(false)
  })

  it('polls when any job is active', () => {
    const jobs = [
      { id: '1', status: 'completed' },
      { id: '2', status: 'extracting' },
    ]
    const hasActive = jobs.some((j) => isActiveJobStatus(j.status))
    expect(hasActive).toBe(true)
  })
})
