import { get, post } from './client'
import type { LoginRequest, RegisterRequest, AuthResponse } from '../../types/auth'
import type { User } from '../../types/user'

export const authApi = {
  login: (data: LoginRequest): Promise<AuthResponse> =>
    post<AuthResponse>('/auth/login', data),

  register: (data: RegisterRequest): Promise<AuthResponse> =>
    post<AuthResponse>('/auth/register', data),

  me: (): Promise<User> =>
    get<User>('/auth/me'),
}
