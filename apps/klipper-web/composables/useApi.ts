export function useApi() {
  const config = useRuntimeConfig()
  const { addToast } = useToast()
  const cookieSecure =
    config.public.cookieSecure === 'true'
      ? true
      : config.public.cookieSecure === 'false'
        ? false
        : import.meta.env.PROD
  const token = useCookie<string | null>('klipper_token', {
    sameSite: 'lax',
    secure: cookieSecure,
    maxAge: 60 * 60 * 24 * 30,
  })

  const apiFetch = $fetch.create({
    baseURL: (import.meta.server
      ? config.apiUrlInternal || config.public.apiUrl
      : config.public.apiUrl) as string,
    onRequest({ options }) {
      if (token.value) {
        options.headers = {
          ...(options.headers as Record<string, string>),
          Authorization: `Bearer ${token.value}`,
        }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        const hadToken = !!token.value
        token.value = null
        if (hadToken) {
          addToast('Sua sessão expirou. Faça login novamente.', 'warn')
        }
        navigateTo('/login')
      }
    },
  })

  return { apiFetch, token }
}
