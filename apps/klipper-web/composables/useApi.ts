const REFRESH_PATH = '/api/v1/auth/refresh'

function isUnauthorized(error: unknown): boolean {
  const failure = error as { response?: { status?: number }; statusCode?: number }
  return (failure?.response?.status ?? failure?.statusCode) === 401
}

export function useApi() {
  const config = useRuntimeConfig()
  const { addToast } = useToast()
  const { track } = useServerWaking()
  const cookieSecure =
    config.public.cookieSecure === 'true'
      ? true
      : config.public.cookieSecure === 'false'
        ? false
        : import.meta.env.PROD
  const token = useCookie<string | null>('klipper_token', {
    sameSite: 'lax',
    secure: cookieSecure,
    maxAge: 60 * 15,
  })

  const rawFetch = $fetch.create({
    baseURL: config.public.apiUrl as string,
    credentials: 'include',
    timeout: 15_000,
    retry: 2,
    retryStatusCodes: [502, 503, 504],
    retryDelay: ({ options }) => 500 * 2 ** (2 - Number(options.retry ?? 0)),
    onRequest({ options }) {
      if (token.value) {
        options.headers = {
          ...(options.headers as unknown as Record<string, string>),
          Authorization: `Bearer ${token.value}`,
        } as unknown as typeof options.headers
      }
    },
  })

  function endSession() {
    const hadToken = !!token.value
    token.value = null
    if (hadToken) {
      addToast('Sua sessão expirou. Faça login novamente.', 'warn')
    }
    navigateTo('/login')
  }

  // O access token dura 15 minutos, então 401 quase sempre é "expirou", não
  // "não autorizado": renova pelo refresh HttpOnly e repete a chamada uma vez,
  // sem o usuário perceber. Só desloga quando o próprio refresh é recusado —
  // deslogar direto no 401 jogaria pra tela de login quem só ficou 15 minutos
  // parado na mesma página.
  async function withRenewal<T>(
    request: Parameters<typeof rawFetch>[0],
    call: () => Promise<T>,
  ): Promise<T> {
    try {
      return await call()
    } catch (error) {
      if (!isUnauthorized(error) || request === REFRESH_PATH) {
        throw error
      }

      try {
        const renewed = await rawFetch<{ token: string }>(REFRESH_PATH, { method: 'POST' })
        token.value = renewed.token
      } catch {
        endSession()
        throw error
      }

      return await call()
    }
  }

  // `raw` passa pela mesma renovação: é por ele que `useTransactions` percorre
  // os cursores, e um 401 no meio da varredura descartaria a lista inteira.
  //
  // `track` fica por fora de tudo: as tentativas de retry e a renovação do
  // token são uma espera só para quem olha a tela, e contá-las em separado
  // faria o aviso de servidor acordando apagar e reacender no meio.
  const apiFetch = Object.assign(
    <T>(
      request: Parameters<typeof rawFetch>[0],
      options?: Parameters<typeof rawFetch>[1],
    ): Promise<T> => track(() => withRenewal(request, () => rawFetch<T>(request, options))),
    {
      raw: <T>(
        request: Parameters<typeof rawFetch.raw>[0],
        options?: Parameters<typeof rawFetch.raw>[1],
      ) => track(() => withRenewal(request, () => rawFetch.raw<T>(request, options))),
    },
  )

  return { apiFetch, token }
}
