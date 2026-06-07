import { useQuery } from '@tanstack/react-query'
import { authApi } from '../lib/api/auth'
import { useAuth } from './useAuth'

export function useCurrentUser() {
  const { isAuthenticated, currentUser } = useAuth()
  const query = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authApi.me,
    enabled: isAuthenticated,
    staleTime: 5 * 60_000,
  })
  return { user: query.data ?? currentUser, ...query }
}
