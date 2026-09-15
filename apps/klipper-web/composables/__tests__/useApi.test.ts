/**
 * useApi tests — SEC-1: o access token dura 15 minutos, então um 401 quase
 * sempre significa "expirou". O cliente renova pelo refresh HttpOnly e repete
 * a chamada sem o usuário perceber; só desloga quando o refresh é recusado.
 *
 * Capturamos a função devolvida por `$fetch.create` para simular as respostas
 * da rede, já que um 401 real exigiria camada HTTP viva.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const mockAddToast = vi.fn()
const mockNavigateTo = vi.fn()
const mockToken = ref<string | null>(null)
const mockTrack = vi.fn(<T>(call: () => Promise<T>) => call())

mockNuxtImport('useToast', () => () => ({ addToast: mockAddToast }))
mockNuxtImport('navigateTo', () => (...args: unknown[]) => mockNavigateTo(...args))
mockNuxtImport('useCookie', () => () => mockToken)
mockNuxtImport('useServerWaking', () => () => ({ track: mockTrack }))

function unauthorizedError() {
  return Object.assign(new Error('Unauthorized'), {
    response: { status: 401 },
    statusCode: 401,
  })
}

describe('useApi', () => {
  let capturedConfig: {
    retry?: number
    retryStatusCodes?: number[]
    retryDelay?: (ctx: { options: { retry?: number } }) => number
    timeout?: number
  }
  let mockRawFetch: ReturnType<typeof vi.fn> & { raw: ReturnType<typeof vi.fn> }

  beforeEach(() => {
    mockAddToast.mockReset()
    mockNavigateTo.mockReset()
    mockTrack.mockClear()
    mockToken.value = null
    mockRawFetch = Object.assign(vi.fn(), { raw: vi.fn() })

    vi.stubGlobal('$fetch', {
      create: vi.fn((config: typeof capturedConfig) => {
        capturedConfig = config
        return mockRawFetch
      }),
    })
  })

  it('renews the token and replays the request when the access token expired', async () => {
    mockToken.value = 'jwt-expirado'
    mockRawFetch
      .mockRejectedValueOnce(unauthorizedError())
      .mockResolvedValueOnce({ token: 'jwt-novo' })
      .mockResolvedValueOnce([{ id: 1 }])

    const { apiFetch } = useApi()
    const data = await apiFetch('/api/v1/transactions')

    expect(data).toEqual([{ id: 1 }])
    expect(mockToken.value).toBe('jwt-novo')
    expect(mockRawFetch).toHaveBeenNthCalledWith(2, '/api/v1/auth/refresh', { method: 'POST' })
    expect(mockNavigateTo).not.toHaveBeenCalled()
    expect(mockAddToast).not.toHaveBeenCalled()
  })

  it('shows a session-expired toast and redirects to /login when the refresh is refused', async () => {
    mockToken.value = 'jwt-expirado'
    mockRawFetch.mockRejectedValue(unauthorizedError())

    const { apiFetch } = useApi()
    await expect(apiFetch('/api/v1/transactions')).rejects.toThrow()

    expect(mockToken.value).toBeNull()
    expect(mockAddToast).toHaveBeenCalledWith('Sua sessão expirou. Faça login novamente.', 'warn')
    expect(mockNavigateTo).toHaveBeenCalledWith('/login')
  })

  it('redirects to /login without a toast when there was no token', async () => {
    mockToken.value = null
    mockRawFetch.mockRejectedValue(unauthorizedError())

    const { apiFetch } = useApi()
    await expect(apiFetch('/api/v1/transactions')).rejects.toThrow()

    expect(mockAddToast).not.toHaveBeenCalled()
    expect(mockNavigateTo).toHaveBeenCalledWith('/login')
  })

  it('renews the token and replays a raw request too', async () => {
    mockToken.value = 'jwt-expirado'
    const page = { _data: [{ id: 1 }], headers: new Headers() }
    mockRawFetch.raw
      .mockRejectedValueOnce(unauthorizedError())
      .mockResolvedValueOnce(page)
    mockRawFetch.mockResolvedValueOnce({ token: 'jwt-novo' })

    const { apiFetch } = useApi()
    const res = await apiFetch.raw('/api/v1/transactions')

    expect(res).toBe(page)
    expect(mockToken.value).toBe('jwt-novo')
    expect(mockNavigateTo).not.toHaveBeenCalled()
  })

  it('never tries to refresh the refresh call itself', async () => {
    mockToken.value = 'jwt-expirado'
    mockRawFetch.mockRejectedValue(unauthorizedError())

    const { apiFetch } = useApi()
    await expect(apiFetch('/api/v1/auth/refresh', { method: 'POST' })).rejects.toThrow()

    expect(mockRawFetch).toHaveBeenCalledTimes(1)
  })

  it('does nothing special for non-401 errors', async () => {
    mockToken.value = 'jwt-token'
    mockRawFetch.mockRejectedValue(
      Object.assign(new Error('Server error'), { response: { status: 500 }, statusCode: 500 })
    )

    const { apiFetch } = useApi()
    await expect(apiFetch('/api/v1/transactions')).rejects.toThrow()

    expect(mockRawFetch).toHaveBeenCalledTimes(1)
    expect(mockAddToast).not.toHaveBeenCalled()
    expect(mockNavigateTo).not.toHaveBeenCalled()
    expect(mockToken.value).toBe('jwt-token')
  })

  it('conta a espera do aviso de servidor acordando, inclusive no raw', async () => {
    mockRawFetch.mockResolvedValueOnce([{ id: 1 }])
    mockRawFetch.raw.mockResolvedValueOnce({ _data: [], headers: new Headers() })

    const { apiFetch } = useApi()
    await apiFetch('/api/v1/transactions')
    await apiFetch.raw('/api/v1/transactions')

    expect(mockTrack).toHaveBeenCalledTimes(2)
  })

  // A espera é uma só do ponto de vista de quem olha a tela: renovar o token
  // no meio não pode apagar e reacender o aviso.
  it('conta uma espera só quando o 401 dispara renovação e repetição', async () => {
    mockToken.value = 'jwt-expirado'
    mockRawFetch
      .mockRejectedValueOnce(unauthorizedError())
      .mockResolvedValueOnce({ token: 'jwt-novo' })
      .mockResolvedValueOnce([{ id: 1 }])

    const { apiFetch } = useApi()
    await apiFetch('/api/v1/transactions')

    expect(mockTrack).toHaveBeenCalledTimes(1)
  })

  it('configures exponential retries for a waking API', () => {
    useApi()

    expect(capturedConfig.retry).toBe(2)
    expect(capturedConfig.retryStatusCodes).toEqual([502, 503, 504])
    expect(capturedConfig.timeout).toBe(15_000)
    expect(capturedConfig.retryDelay?.({ options: { retry: 2 } })).toBe(500)
    expect(capturedConfig.retryDelay?.({ options: { retry: 1 } })).toBe(1000)
  })
})
