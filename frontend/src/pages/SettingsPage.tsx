import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { Settings2, RotateCcw, Plus, ChevronDown, ChevronRight, Save, Undo2 } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { PermissionDeniedCard } from '../components/common/PermissionDeniedCard'
import { SeverityBadge } from '../components/common/SeverityBadge'
import { formatDate } from '../lib/utils'
import {
  useRiskRules,
  useInitializeRiskRules,
  useResetRiskRuleDefaults,
  useUpdateRiskRule,
  useBulkUpdateRiskRules,
} from '../hooks/useRiskRules'
import { canConfigureRiskRules } from '../lib/auth/permissions'
import type { RiskRuleConfig, BulkUpdateRiskRuleConfigItem } from '../types/riskRule'
import type { RiskSeverity } from '../types/risk'

// ─── RuleRow ─────────────────────────────────────────────────────────────────

interface RuleRowProps {
  rule: RiskRuleConfig
  canConfig: boolean
  workspaceId: string
  onDirtyChange: (ruleKey: string, data: BulkUpdateRiskRuleConfigItem | null) => void
}

function RuleRow({ rule, canConfig, workspaceId, onDirtyChange }: RuleRowProps) {
  const [isEnabled, setIsEnabled] = useState(rule.is_enabled)
  const [thresholdAmount, setThresholdAmount] = useState<string>(
    rule.threshold_amount != null ? String(rule.threshold_amount) : '',
  )
  const [thresholdPercent, setThresholdPercent] = useState<string>(
    rule.threshold_percent != null ? String(rule.threshold_percent) : '',
  )
  const [showAdvanced, setShowAdvanced] = useState(false)
  const updateRule = useUpdateRiskRule(workspaceId)

  useEffect(() => {
    setIsEnabled(rule.is_enabled)
    setThresholdAmount(rule.threshold_amount != null ? String(rule.threshold_amount) : '')
    setThresholdPercent(rule.threshold_percent != null ? String(rule.threshold_percent) : '')
  }, [rule.is_enabled, rule.threshold_amount, rule.threshold_percent])

  const currentAmount = thresholdAmount !== '' ? Number(thresholdAmount) : null
  const currentPercent = thresholdPercent !== '' ? Number(thresholdPercent) : null
  const isDirty =
    isEnabled !== rule.is_enabled ||
    currentAmount !== (rule.threshold_amount ?? null) ||
    currentPercent !== (rule.threshold_percent ?? null)

  useEffect(() => {
    onDirtyChange(
      rule.rule_key,
      isDirty
        ? { rule_key: rule.rule_key, is_enabled: isEnabled, threshold_amount: currentAmount, threshold_percent: currentPercent }
        : null,
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDirty, isEnabled, currentAmount, currentPercent, rule.rule_key])

  const handleToggle = () => {
    if (!canConfig) return
    setIsEnabled((v) => !v)
  }

  const handleSave = () => {
    updateRule.mutate(
      { configId: rule.id, data: { is_enabled: isEnabled, threshold_amount: currentAmount, threshold_percent: currentPercent } },
      {
        onSuccess: (updated) => {
          setIsEnabled(updated.is_enabled)
          setThresholdAmount(updated.threshold_amount != null ? String(updated.threshold_amount) : '')
          setThresholdPercent(updated.threshold_percent != null ? String(updated.threshold_percent) : '')
          onDirtyChange(rule.rule_key, null)
        },
      },
    )
  }

  return (
    <div className={`bg-white border rounded-xl p-5 shadow-card transition-colors ${isDirty ? 'border-blue-300 ring-1 ring-blue-200' : 'border-slate-200'}`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm font-semibold text-slate-900 font-mono">{rule.rule_key}</p>
            <SeverityBadge severity={rule.severity as RiskSeverity} />
            <span className="text-xs text-slate-500">{rule.risk_type.replace(/_/g, ' ')}</span>
            {isDirty && (
              <span className="text-xs text-blue-700 font-medium bg-blue-50 px-1.5 py-0.5 rounded">unsaved</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-slate-500">{isEnabled ? 'Enabled' : 'Disabled'}</span>
          <button
            role="switch"
            aria-checked={isEnabled}
            onClick={handleToggle}
            disabled={!canConfig || updateRule.isPending}
            className={`relative inline-flex h-5 w-9 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer ${isEnabled ? 'bg-blue-600' : 'bg-slate-200'}`}
          >
            <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${isEnabled ? 'translate-x-4' : 'translate-x-0'}`} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label className="text-xs text-slate-500 font-medium mb-1 block">Threshold Amount (₹)</label>
          <input
            type="number"
            value={thresholdAmount}
            onChange={(e) => setThresholdAmount(e.target.value)}
            disabled={!canConfig}
            placeholder="—"
            className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
        <div>
          <label className="text-xs text-slate-500 font-medium mb-1 block">Threshold %</label>
          <input
            type="number"
            value={thresholdPercent}
            onChange={(e) => setThresholdPercent(e.target.value)}
            disabled={!canConfig}
            placeholder="—"
            className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
      </div>

      {canConfig && isDirty && (
        <button
          onClick={handleSave}
          disabled={updateRule.isPending}
          className="mb-3 px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {updateRule.isPending ? 'Saving…' : 'Save This Rule'}
        </button>
      )}

      {rule.config_data && Object.keys(rule.config_data).length > 0 && (
        <div className="border-t border-slate-100 pt-3">
          <button
            onClick={() => setShowAdvanced((v) => !v)}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 cursor-pointer"
          >
            {showAdvanced ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            Advanced config
          </button>
          {showAdvanced && (
            <div className="mt-2 bg-slate-50 rounded-lg p-3 space-y-1.5">
              {Object.entries(rule.config_data).map(([k, v]) => (
                <div key={k} className="grid grid-cols-[140px_1fr] gap-2 text-xs">
                  <span className="text-slate-500 font-medium">{k.replace(/_/g, ' ')}</span>
                  <span className="text-slate-800 break-all">{String(v)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export function SettingsPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const { currentUser, logout, currentWorkspaceRole } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)
  const role = derivedRole ?? currentWorkspaceRole

  const { data: rules, isLoading, error, refetch } = useRiskRules(workspaceId)
  const initRules = useInitializeRiskRules(workspaceId)
  const resetRules = useResetRiskRuleDefaults(workspaceId)
  const bulkUpdate = useBulkUpdateRiskRules(workspaceId)
  const canConfig = canConfigureRiskRules(role)

  const dirtyRowsRef = useRef<Map<string, BulkUpdateRiskRuleConfigItem>>(new Map())
  const [hasDirty, setHasDirty] = useState(false)
  const [revisionKey, setRevisionKey] = useState(0)

  const handleDirtyChange = useCallback(
    (ruleKey: string, data: BulkUpdateRiskRuleConfigItem | null) => {
      if (data) {
        dirtyRowsRef.current.set(ruleKey, data)
      } else {
        dirtyRowsRef.current.delete(ruleKey)
      }
      setHasDirty(dirtyRowsRef.current.size > 0)
    },
    [],
  )

  const handleSaveAll = () => {
    const configs = Array.from(dirtyRowsRef.current.values())
    if (configs.length === 0) return
    bulkUpdate.mutate(
      { configs },
      {
        onSuccess: () => {
          dirtyRowsRef.current.clear()
          setHasDirty(false)
          setRevisionKey((k) => k + 1)
        },
      },
    )
  }

  const handleDiscardAll = () => {
    dirtyRowsRef.current.clear()
    setHasDirty(false)
    setRevisionKey((k) => k + 1)
  }

  const prevRulesRef = useRef(rules)
  useEffect(() => {
    if (rules !== prevRulesRef.current) {
      prevRulesRef.current = rules
      dirtyRowsRef.current.clear()
      setHasDirty(false)
    }
  }, [rules])

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <PageHeader title="Settings" subtitle="Manage your account and workspace configuration" />

      {/* ── Profile ── */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-card mb-4">
        <h2 className="text-base font-semibold text-slate-900 mb-4">Profile</h2>
        <dl className="space-y-3">
          <div className="flex items-center justify-between">
            <dt className="text-sm font-medium text-slate-500">Name</dt>
            <dd className="text-sm text-slate-900">{currentUser?.full_name ?? '—'}</dd>
          </div>
          <div className="flex items-center justify-between">
            <dt className="text-sm font-medium text-slate-500">Email</dt>
            <dd className="text-sm text-slate-900">{currentUser?.email}</dd>
          </div>
          <div className="flex items-center justify-between">
            <dt className="text-sm font-medium text-slate-500">Member since</dt>
            <dd className="text-sm text-slate-900">
              {currentUser?.created_at ? formatDate(currentUser.created_at) : '—'}
            </dd>
          </div>
        </dl>
      </div>

      {/* ── Risk Rule Configuration ── */}
      {workspaceId && (
        <div>
          <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Risk Rule Configuration</h2>
              <p className="text-sm text-slate-500 mt-0.5">
                Customize detection thresholds and rule settings for this workspace
              </p>
            </div>
            {canConfig && (
              <div className="flex items-center gap-2 flex-wrap">
                {(!rules || rules.length === 0) && (
                  <button
                    onClick={() => initRules.mutate()}
                    disabled={initRules.isPending}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    <Plus className="w-4 h-4" />
                    {initRules.isPending ? 'Initializing…' : 'Initialize Rules'}
                  </button>
                )}
                {rules && rules.length > 0 && hasDirty && (
                  <>
                    <button
                      onClick={handleDiscardAll}
                      disabled={bulkUpdate.isPending}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      <Undo2 className="w-4 h-4" />
                      Discard Changes
                    </button>
                    <button
                      onClick={handleSaveAll}
                      disabled={bulkUpdate.isPending}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      <Save className="w-4 h-4" />
                      {bulkUpdate.isPending
                        ? 'Saving…'
                        : `Save All Changes (${dirtyRowsRef.current.size})`}
                    </button>
                  </>
                )}
                {rules && rules.length > 0 && (
                  <button
                    onClick={() => resetRules.mutate()}
                    disabled={resetRules.isPending}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-200 rounded-xl hover:bg-red-50 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    <RotateCcw className="w-4 h-4" />
                    {resetRules.isPending ? 'Resetting…' : 'Reset to Defaults'}
                  </button>
                )}
              </div>
            )}
          </div>

          {!canConfig && (
            <PermissionDeniedCard
              message="You need owner or admin role to configure risk rules."
              requiredRoles={['owner', 'admin']}
              className="mb-4"
            />
          )}

          {!canConfig && role !== null && (
            <div className="mb-4 p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-500">
              Risk rule settings are read-only for your role. Contact an owner or admin to make changes.
            </div>
          )}

          {bulkUpdate.isError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              Failed to save all changes. Your edits are preserved — try again.
            </div>
          )}

          {isLoading && <LoadingState />}
          {!!error && <ErrorState error={error as Error} onRetry={() => refetch()} className="mb-4" />}

          {!isLoading && !error && (!rules || rules.length === 0) && (
            <EmptyState
              icon={<Settings2 className="w-12 h-12" />}
              title="No risk rules configured"
              body="Initialize rules to customize risk detection thresholds for this workspace."
              action={
                canConfig ? (
                  <button
                    onClick={() => initRules.mutate()}
                    disabled={initRules.isPending}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer disabled:opacity-60"
                  >
                    <Plus className="w-4 h-4" />
                    Initialize Rules
                  </button>
                ) : undefined
              }
            />
          )}

          {!isLoading && rules && rules.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {rules.map((rule) => (
                <RuleRow
                  key={`${rule.id}-${revisionKey}`}
                  rule={rule}
                  canConfig={canConfig}
                  workspaceId={workspaceId}
                  onDirtyChange={handleDirtyChange}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Sign out ── */}
      <div className="bg-white border border-red-200 rounded-xl p-6 shadow-card mt-8">
        <h2 className="text-base font-semibold text-red-700 mb-2">Sign out</h2>
        <p className="text-sm text-slate-500 mb-4">
          You will be redirected to the login page.
        </p>
        <button
          onClick={logout}
          className="px-4 py-2 text-sm font-semibold text-white bg-red-600 hover:bg-red-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Sign out
        </button>
      </div>
    </div>
  )
}
