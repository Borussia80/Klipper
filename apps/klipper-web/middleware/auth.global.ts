const PUBLIC_ROUTES = ['/login', '/onboarding']

export default defineNuxtRouteMiddleware((to) => {
  const token = useCookie('klipper_token')

  if (!token.value && !PUBLIC_ROUTES.includes(to.path)) {
    return navigateTo('/login')
  }

  if (token.value && to.path === '/login') {
    return navigateTo('/dashboard')
  }
})
