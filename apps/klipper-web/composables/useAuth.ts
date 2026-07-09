interface User {
  id: number
  email: string
  name: string | null
}

interface AuthResponse {
  token: string
  user: User
}

export function useAuth() {
  const { apiFetch, token } = useApi()
  const user = useState<User | null>('auth.user', () => null)

  async function login(email: string, password: string) {
    const data = await apiFetch<AuthResponse>('/api/v1/auth/sign_in', {
      method: 'POST',
      body: { email, password },
    })
    token.value = data.token
    user.value = data.user
    await navigateTo('/dashboard')
  }

  async function signUp(email: string, password: string, name?: string) {
    const data = await apiFetch<AuthResponse>('/api/v1/auth/sign_up', {
      method: 'POST',
      body: { email, password, name },
    })
    token.value = data.token
    user.value = data.user
    await navigateTo('/dashboard')
  }

  async function logout() {
    try {
      await apiFetch('/api/v1/users/logout', { method: 'POST' })
    } catch {
      // best-effort: revoke server-side if possible, but always clear local session
    }
    token.value = null
    user.value = null
    await navigateTo('/login')
  }

  async function fetchCurrentUser() {
    user.value = await apiFetch<User>('/api/v1/users/me')
  }

  const isAuthenticated = computed(() => !!token.value)

  return { user, login, signUp, logout, fetchCurrentUser, isAuthenticated }
}
