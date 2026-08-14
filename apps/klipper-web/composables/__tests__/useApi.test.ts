/**
 * useApi tests — UX-2: a 401 response should surface a "session expired" toast
 * before redirecting to /login, but only when there was a token to begin with.
 *
 * We capture the config object passed to `$fetch.create` and invoke its
 * `onResponseError` hook directly, since triggering a real 401 would require
 * a live HTTP layer.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const mockAddToast = vi.fn()
const mockNavigateTo = vi.fn()
const mockToken = ref<string | null>(null)

mockNuxtImport('useToast', () => () => ({ addToast: mockAddToast }))
mockNuxtImport('navigateTo', () => (...args: unknown[]) => mockNavigateTo(...args))
mockNuxtImport('useCookie', () => () => mockToken)

describe('useApi', () => {
  let capturedConfig: { onResponseError: (ctx: { response: { status: number } }) => void }

  beforeEach(() => {
    mockAddToast.mockReset()
    mockNavigateTo.mockReset()
    mockToken.value = null

    vi.stubGlobal('$fetch', {
      create: vi.fn((config: typeof capturedConfig) => {
        capturedConfig = config
        return vi.fn()
      }),
    })
  })

  it('shows a session-expired toast and redirects to /login on 401 when a token was present', () => {
    mockToken.value = 'jwt-token'
    useApi()

    capturedConfig.onResponseError({ response: { status: 401 } })

    expect(mockToken.value).toBeNull()
    expect(mockAddToast).toHaveBeenCalledWith('Sua sessão expirou. Faça login novamente.', 'warn')
    expect(mockNavigateTo).toHaveBeenCalledWith('/login')
  })

  it('redirects to /login on 401 without a toast when there was no token', () => {
    mockToken.value = null
    useApi()

    capturedConfig.onResponseError({ response: { status: 401 } })

    expect(mockAddToast).not.toHaveBeenCalled()
    expect(mockNavigateTo).toHaveBeenCalledWith('/login')
  })

  it('does nothing special for non-401 errors', () => {
    mockToken.value = 'jwt-token'
    useApi()

    capturedConfig.onResponseError({ response: { status: 500 } })

    expect(mockAddToast).not.toHaveBeenCalled()
    expect(mockNavigateTo).not.toHaveBeenCalled()
    expect(mockToken.value).toBe('jwt-token')
  })
})
