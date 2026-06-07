import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import type { User } from '../types/user'
import {
  getToken,
  setToken,
  clearAuth,
  setStoredUser,
} from '../lib/auth/tokenStorage'
import { authApi } from '../lib/api/auth'
import type { WorkspaceRole } from '../types/workspaceMember'
import { CURRENT_WORKSPACE_KEY } from '../lib/constants'

interface AuthContextValue {
  currentUser: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  currentWorkspaceId: string | null
  currentWorkspaceRole: WorkspaceRole | null
  login: (token: string, user: User) => void
  logout: () => void
  setCurrentWorkspace: (workspaceId: string | null, role?: WorkspaceRole | null) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [token, setTokenState] = useState<string | null>(getToken)
  const [isLoading, setIsLoading] = useState(true)
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState<string | null>(() => {
    try {
      return localStorage.getItem(CURRENT_WORKSPACE_KEY)
    } catch {
      return null
    }
  })
  const [currentWorkspaceRole, setCurrentWorkspaceRole] = useState<WorkspaceRole | null>(null)

  // On mount: attempt to restore session via /auth/me
  useEffect(() => {
    const storedToken = getToken()
    if (!storedToken) {
      setIsLoading(false)
      return
    }

    authApi
      .me()
      .then((user: User) => {
        setCurrentUser(user)
        setTokenState(storedToken)
      })
      .catch(() => {
        // 401 interceptor already clears token + redirects
        setCurrentUser(null)
        setTokenState(null)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [])

  const login = useCallback((accessToken: string, user: User) => {
    setToken(accessToken)
    setStoredUser(user)
    setTokenState(accessToken)
    setCurrentUser(user)
  }, [])

  const logout = useCallback(() => {
    clearAuth()
    setTokenState(null)
    setCurrentUser(null)
    setCurrentWorkspaceId(null)
    setCurrentWorkspaceRole(null)
    try {
      localStorage.removeItem(CURRENT_WORKSPACE_KEY)
    } catch {
      // Ignore
    }
    window.location.href = '/login'
  }, [])

  const setCurrentWorkspace = useCallback(
    (workspaceId: string | null, role?: WorkspaceRole | null) => {
      setCurrentWorkspaceId(workspaceId)
      setCurrentWorkspaceRole((prevRole) => {
        if (!workspaceId) return null
        if (role !== undefined) return role
        return workspaceId === currentWorkspaceId ? prevRole : null
      })
      try {
        if (workspaceId) {
          localStorage.setItem(CURRENT_WORKSPACE_KEY, workspaceId)
        } else {
          localStorage.removeItem(CURRENT_WORKSPACE_KEY)
        }
      } catch {
        // Ignore
      }
    },
    [currentWorkspaceId],
  )

  const value: AuthContextValue = {
    currentUser,
    token,
    isAuthenticated: !!currentUser && !!token,
    isLoading,
    currentWorkspaceId,
    currentWorkspaceRole,
    login,
    logout,
    setCurrentWorkspace,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

// Export context for advanced use cases
export { AuthContext }
export type { AuthContextValue }
