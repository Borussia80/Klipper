/**
 * useAuth tests — login/signUp/logout state transitions and API calls.
 *
 * We mock `useApi` and `navigateTo` via mockNuxtImport so the composable
 * never makes real HTTP calls or real navigation.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const mockApiFetch = vi.fn()
const mockNavigateTo = vi.fn()
const mockToken = ref<string | null>(null)

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: mockToken,
}))

mockNuxtImport('navigateTo', () => (...args: unknown[]) => mockNavigateTo(...args))

describe('useAuth', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockNavigateTo.mockReset()
    mockToken.value = null
    useAuth().user.value = null
  })

  describe('login', () => {
    it('stores the token and user, then navigates to /dashboard', async () => {
      mockApiFetch.mockResolvedValue({
        token: 'jwt-token',
        user: { id: 1, email: 'user@example.com', name: 'User' },
      })
      const { login, user } = useAuth()

      await login('user@example.com', 'senha1234')

      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/auth/sign_in', {
        method: 'POST',
        body: { email: 'user@example.com', password: 'senha1234' },
      })
      expect(mockToken.value).toBe('jwt-token')
      expect(user.value).toEqual({ id: 1, email: 'user@example.com', name: 'User' })
      expect(mockNavigateTo).toHaveBeenCalledWith('/dashboard')
    })

    it('propagates errors without touching state', async () => {
      mockApiFetch.mockRejectedValue({ data: { error: 'E-mail ou senha inválidos' } })
      const { login, user } = useAuth()

      await expect(login('user@example.com', 'wrong')).rejects.toBeTruthy()
      expect(user.value).toBeNull()
      expect(mockNavigateTo).not.toHaveBeenCalled()
    })
  })

  describe('signUp', () => {
    it('creates the account, stores the session, then navigates to /dashboard', async () => {
      mockApiFetch.mockResolvedValue({
        token: 'jwt-token-new',
        user: { id: 2, email: 'new@example.com', name: 'Novo' },
      })
      const { signUp, user } = useAuth()

      await signUp('new@example.com', 'senha1234', 'Novo')

      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/auth/sign_up', {
        method: 'POST',
        body: { email: 'new@example.com', password: 'senha1234', name: 'Novo' },
      })
      expect(mockToken.value).toBe('jwt-token-new')
      expect(user.value).toEqual({ id: 2, email: 'new@example.com', name: 'Novo' })
      expect(mockNavigateTo).toHaveBeenCalledWith('/dashboard')
    })

    it('propagates validation errors without creating a session', async () => {
      mockApiFetch.mockRejectedValue({ data: { errors: ['E-mail já está em uso'] } })
      const { signUp, user } = useAuth()

      await expect(signUp('taken@example.com', 'senha1234')).rejects.toBeTruthy()
      expect(user.value).toBeNull()
      expect(mockToken.value).toBeNull()
      expect(mockNavigateTo).not.toHaveBeenCalled()
    })
  })

  describe('logout', () => {
    it('calls the backend logout endpoint, clears token and user, then navigates to /login', async () => {
      mockApiFetch.mockResolvedValue({ message: 'Sessão encerrada' })
      mockToken.value = 'jwt-token'
      const { logout, user } = useAuth()
      user.value = { id: 1, email: 'user@example.com', name: 'User' }

      await logout()

      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/users/logout', { method: 'POST' })
      expect(mockToken.value).toBeNull()
      expect(user.value).toBeNull()
      expect(mockNavigateTo).toHaveBeenCalledWith('/login')
    })

    it('clears local session even when the backend call fails', async () => {
      mockApiFetch.mockRejectedValue({ data: { error: 'Não autorizado' } })
      mockToken.value = 'jwt-token'
      const { logout, user } = useAuth()
      user.value = { id: 1, email: 'user@example.com', name: 'User' }

      await logout()

      expect(mockToken.value).toBeNull()
      expect(user.value).toBeNull()
      expect(mockNavigateTo).toHaveBeenCalledWith('/login')
    })
  })

  describe('fetchCurrentUser', () => {
    it('populates user from GET /api/v1/users/me', async () => {
      mockApiFetch.mockResolvedValue({ id: 3, email: 'saved@example.com', name: 'Saved' })
      const { fetchCurrentUser, user } = useAuth()

      await fetchCurrentUser()

      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/users/me')
      expect(user.value).toEqual({ id: 3, email: 'saved@example.com', name: 'Saved' })
    })

    it('propagates errors without swallowing them (caller decides how to handle)', async () => {
      mockApiFetch.mockRejectedValue({ data: { error: 'Não autorizado' } })
      const { fetchCurrentUser, user } = useAuth()

      await expect(fetchCurrentUser()).rejects.toBeTruthy()
      expect(user.value).toBeNull()
    })
  })

  describe('isAuthenticated', () => {
    it('is false without a token and true once one is set', () => {
      const { isAuthenticated } = useAuth()
      expect(isAuthenticated.value).toBe(false)

      mockToken.value = 'jwt-token'
      expect(isAuthenticated.value).toBe(true)
    })
  })
})
