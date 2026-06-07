import { useNavigate, useParams } from 'react-router-dom'
import { RefreshCw, Settings, LogOut, ChevronDown } from 'lucide-react'
import { motion, AnimatePresence, useReducedMotion } from 'motion/react'
import { useAuth } from '../../hooks/useAuth'
import { useQueryClient } from '@tanstack/react-query'
import { WorkspaceSwitcher } from './WorkspaceSwitcher'
import { useState } from 'react'
import { cn } from '../../lib/utils'

export function Topbar() {
  const { currentUser, logout, currentWorkspaceId: authWorkspaceId } = useAuth()
  const { workspaceId: urlWorkspaceId } = useParams<{ workspaceId?: string }>()
  const qc = useQueryClient()
  const navigate = useNavigate()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const prefersReduced = useReducedMotion() ?? false

  const workspaceId = urlWorkspaceId ?? authWorkspaceId ?? undefined

  const handleRefresh = () => {
    setRefreshing(true)
    qc.invalidateQueries()
    setTimeout(() => setRefreshing(false), 800)
  }

  const initials = currentUser
    ? (currentUser.full_name ?? currentUser.email)
        .split(' ')
        .map((p: string) => p[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : '?'

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3 flex-shrink-0 shadow-[0_1px_0_0_#e2e8f0]">
      {/* Workspace switcher */}
      <div className="flex-1 min-w-0">
        <WorkspaceSwitcher workspaceId={workspaceId} />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-0.5">
        <button
          onClick={handleRefresh}
          className="p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
          title="Refresh data"
          aria-label="Refresh data"
        >
          <RefreshCw
            className={cn('w-4 h-4', refreshing && !prefersReduced && 'animate-spin')}
          />
        </button>

        <button
          onClick={() => navigate(workspaceId ? `/workspaces/${workspaceId}/settings` : '/dashboard')}
          className="p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
          title="Settings"
          aria-label="Settings"
        >
          <Settings className="w-4 h-4" />
        </button>

        {/* User menu */}
        <div className="relative ml-1">
          <button
            onClick={() => setUserMenuOpen((o) => !o)}
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-100 transition-colors duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
            aria-haspopup="true"
            aria-expanded={userMenuOpen}
          >
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
              {initials}
            </div>
            <span className="text-sm font-medium text-slate-700 max-w-[120px] truncate hidden sm:block">
              {currentUser?.full_name ?? currentUser?.email ?? 'User'}
            </span>
            <ChevronDown
              className={cn(
                'w-3.5 h-3.5 text-slate-400 hidden sm:block transition-transform duration-150',
                userMenuOpen && 'rotate-180',
              )}
            />
          </button>

          <AnimatePresence>
            {userMenuOpen && (
              <>
                {/* Backdrop */}
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setUserMenuOpen(false)}
                />
                <motion.div
                  initial={{ opacity: 0, y: -4, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -4, scale: 0.97 }}
                  transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
                  className={cn(
                    'absolute right-0 top-full mt-1.5 w-56 bg-white border border-slate-200 rounded-xl shadow-card-lg z-20 py-1 overflow-hidden',
                  )}
                >
                  <div className="px-4 py-2.5 border-b border-slate-100">
                    <p className="text-xs font-semibold text-slate-800 truncate">
                      {currentUser?.full_name ?? 'User'}
                    </p>
                    <p className="text-xs text-slate-500 truncate mt-0.5">{currentUser?.email}</p>
                  </div>
                  <button
                    onClick={() => {
                      setUserMenuOpen(false)
                      navigate(workspaceId ? `/workspaces/${workspaceId}/settings` : '/dashboard')
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors duration-100 cursor-pointer"
                  >
                    <Settings className="w-4 h-4 text-slate-400" />
                    Settings
                  </button>
                  <button
                    onClick={() => {
                      setUserMenuOpen(false)
                      logout()
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors duration-100 cursor-pointer"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign out
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  )
}
