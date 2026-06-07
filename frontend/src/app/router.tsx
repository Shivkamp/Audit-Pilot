import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { ProtectedRoute } from '../components/auth/ProtectedRoute'
import { PublicOnlyRoute } from '../components/auth/PublicOnlyRoute'
import { PageLoadingState } from '../components/common/LoadingState'

// Auth pages — keep eager (small, always needed)
import { LoginPage } from '../pages/auth/LoginPage'
import { RegisterPage } from '../pages/auth/RegisterPage'
import { NotFoundPage } from '../pages/NotFoundPage'

// Heavy app pages — lazy loaded
const LandingPage = lazy(() => import('../pages/LandingPage').then((m) => ({ default: m.LandingPage })))
const DashboardPage = lazy(() => import('../pages/DashboardPage').then((m) => ({ default: m.DashboardPage })))
const ClientsPage = lazy(() => import('../pages/ClientsPage').then((m) => ({ default: m.ClientsPage })))
const WorkspacesPage = lazy(() => import('../pages/WorkspacesPage').then((m) => ({ default: m.WorkspacesPage })))
const WorkspaceDashboardPage = lazy(() => import('../pages/WorkspaceDashboardPage').then((m) => ({ default: m.WorkspaceDashboardPage })))
const DocumentsPage = lazy(() => import('../pages/DocumentsPage').then((m) => ({ default: m.DocumentsPage })))
const JobsPage = lazy(() => import('../pages/JobsPage').then((m) => ({ default: m.JobsPage })))
const RiskFindingsPage = lazy(() => import('../pages/RiskFindingsPage').then((m) => ({ default: m.RiskFindingsPage })))
const KnowledgeSearchPage = lazy(() => import('../pages/KnowledgeSearchPage').then((m) => ({ default: m.KnowledgeSearchPage })))
const AgentChatPage = lazy(() => import('../pages/AgentChatPage').then((m) => ({ default: m.AgentChatPage })))
const WorkspaceMembersPage = lazy(() => import('../pages/WorkspaceMembersPage').then((m) => ({ default: m.WorkspaceMembersPage })))
const SettingsPage = lazy(() => import('../pages/SettingsPage').then((m) => ({ default: m.SettingsPage })))
const ForbiddenPage = lazy(() => import('../pages/ForbiddenPage').then((m) => ({ default: m.ForbiddenPage })))

function LazyRoute({ element }: { element: React.ReactNode }) {
  return <Suspense fallback={<PageLoadingState />}>{element}</Suspense>
}

export const router = createBrowserRouter([
  // Public-only routes (redirect to /dashboard if already authed)
  {
    element: <PublicOnlyRoute />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },

  // Protected app routes
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: '/dashboard', element: <LazyRoute element={<DashboardPage />} /> },
          { path: '/clients', element: <LazyRoute element={<ClientsPage />} /> },
          { path: '/clients/:clientId/workspaces', element: <LazyRoute element={<WorkspacesPage />} /> },
          { path: '/workspaces/:workspaceId', element: <LazyRoute element={<WorkspaceDashboardPage />} /> },
          { path: '/workspaces/:workspaceId/documents', element: <LazyRoute element={<DocumentsPage />} /> },
          { path: '/workspaces/:workspaceId/jobs', element: <LazyRoute element={<JobsPage />} /> },
          { path: '/workspaces/:workspaceId/risks', element: <LazyRoute element={<RiskFindingsPage />} /> },
          { path: '/workspaces/:workspaceId/knowledge', element: <LazyRoute element={<KnowledgeSearchPage />} /> },
          { path: '/workspaces/:workspaceId/agent', element: <LazyRoute element={<AgentChatPage />} /> },
          { path: '/workspaces/:workspaceId/members', element: <LazyRoute element={<WorkspaceMembersPage />} /> },
          { path: '/workspaces/:workspaceId/settings', element: <LazyRoute element={<SettingsPage />} /> },
          { path: '/403', element: <LazyRoute element={<ForbiddenPage />} /> },
        ],
      },
    ],
  },

  // Root: public landing page (accessible to all)
  { index: true, path: '/', element: <LazyRoute element={<LandingPage />} /> },
  // /landing alias → redirect to /
  { path: '/landing', element: <Navigate to="/" replace /> },

  // 404
  { path: '*', element: <NotFoundPage /> },
])

// Outlet re-export for nested usage
export { Outlet }
