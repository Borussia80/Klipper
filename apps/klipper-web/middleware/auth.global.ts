const PUBLIC_ROUTES = ['/login', '/onboarding']

export default defineNuxtRouteMiddleware(async (to) => {
  const token = useCookie('klipper_token')

  if (!token.value && !PUBLIC_ROUTES.includes(to.path)) {
    try {
      const { apiFetch } = useApi()
      const data = await apiFetch<{ token: string }>('/api/v1/auth/refresh', { method: 'POST' })
      token.value = data.token
    } catch {
      return navigateTo('/login')
    }
  }

  if (token.value && to.path === '/login') {
    return navigateTo('/dashboard')
  }
})
