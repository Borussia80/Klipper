export function useApi() {
  const config = useRuntimeConfig()
  const { addToast } = useToast()
  const token = useCookie<string | null>('klipper_token', {
    sameSite: 'lax',
    secure: import.meta.env.PROD,
    maxAge: 60 * 60 * 24 * 30,
  })

  const apiFetch = $fetch.create({
    baseURL: config.public.apiUrl as string,
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
