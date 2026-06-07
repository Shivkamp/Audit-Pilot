import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import toast from 'react-hot-toast'
import { getToken, clearAuth } from '../auth/tokenStorage'
import { CURRENT_WORKSPACE_KEY } from '../constants'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// ─── Request interceptor: attach Bearer token ────────────────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ─── Response interceptor: handle 401 and 403 ───────────────────────────────
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response) {
      const status = error.response.status

      if (status === 401) {
        clearAuth()
        try {
          localStorage.removeItem(CURRENT_WORKSPACE_KEY)
        } catch {
          // Ignore storage errors
        }
        toast.error('Session expired. Please sign in again.')
        // Redirect to login — use window.location to avoid circular React Router dependency
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
      }
      // 403: do NOT logout, caller handles permission-denied UI
    }
    return Promise.reject(error)
  },
)

// ─── Envelope unwrap helper ─────────────────────────────────────────────────
// All backend success responses are shaped as { success, message, data: T }.
// These helpers unwrap the envelope so callers receive T directly.
function unwrap<T>(res: AxiosResponse<{ data: T }>): T {
  return res.data.data
}

// ─── Typed helpers ───────────────────────────────────────────────────────────
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const res = await apiClient.get<{ data: T }>(url, config)
  return unwrap(res)
}

export async function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const res = await apiClient.post<{ data: T }>(url, data, config)
  return unwrap(res)
}

export async function patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const res = await apiClient.patch<{ data: T }>(url, data, config)
  return unwrap(res)
}

export async function del<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const res = await apiClient.delete<{ data: T }>(url, config)
  return unwrap(res)
}
