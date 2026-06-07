import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import type { WorkspaceRole } from '@/types/workspaceMember'

interface AuthState {
  isAuthenticated?: boolean
  currentUser?: { id: string; email: string } | null
  currentWorkspaceRole?: WorkspaceRole | null
}

interface RenderWithProvidersOptions extends RenderOptions {
  auth?: AuthState
  initialRoute?: string
}

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({
    isAuthenticated: true,
    currentUser: { id: 'test-user-id', email: 'test@example.com' },
    currentWorkspaceRole: null,
    login: vi.fn(),
    logout: vi.fn(),
  })),
}))

// jsdom does not implement scrollIntoView
Element.prototype.scrollIntoView = vi.fn()

// Import the mocked hook for per-test overrides
import { useAuth } from '@/hooks/useAuth'

export function renderWithProviders(
  ui: React.ReactElement,
  { auth = {}, initialRoute = '/', ...renderOptions }: RenderWithProvidersOptions = {},
) {
  // Override auth mock values
  vi.mocked(useAuth).mockReturnValue({
    isAuthenticated: auth.isAuthenticated ?? true,
    currentUser: auth.currentUser ?? { id: 'test-user-id', email: 'test@example.com' },
    currentWorkspaceRole: auth.currentWorkspaceRole ?? null,
    login: vi.fn(),
    logout: vi.fn(),
  } as unknown as ReturnType<typeof useAuth>)

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[initialRoute]}>{children}</MemoryRouter>
      </QueryClientProvider>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}
