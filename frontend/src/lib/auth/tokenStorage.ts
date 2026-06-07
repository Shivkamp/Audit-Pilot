import { TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '../constants'
import type { User } from '../../types/user'

// In-memory token store (primary, cleared on tab close)
let _memoryToken: string | null = null

export function getToken(): string | null {
  if (_memoryToken) return _memoryToken
  // Fall back to localStorage on fresh load
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

export function setToken(token: string): void {
  _memoryToken = token
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
  } catch {
    // Ignore storage errors (e.g. private browsing with full quota)
  }
}

export function clearToken(): void {
  _memoryToken = null
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  } catch {
    // Ignore
  }
}

export function getStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function setStoredUser(user: User): void {
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  } catch {
    // Ignore
  }
}

export function clearStoredUser(): void {
  try {
    localStorage.removeItem(USER_STORAGE_KEY)
  } catch {
    // Ignore
  }
}

export function clearAuth(): void {
  clearToken()
  clearStoredUser()
}
