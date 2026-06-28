import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const mockApiFetch = vi.fn()

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: { value: 'test-token' },
}))

describe('useImport', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApiFetch.mockResolvedValue({ imported: 0, errors: [] })
  })

  it('sets result state on successful upload', async () => {
    mockApiFetch.mockResolvedValue({ imported: 3, errors: [] })
    const { useImport } = await import('../useImport')
    const { result, uploadFile } = useImport()
    const file = new File(['content'], 'extrato.csv', { type: 'text/csv' })
    await uploadFile(file)
    expect(result.value?.imported).toBe(3)
    expect(result.value?.errors).toHaveLength(0)
  })

  it('sends FormData with file to /api/v1/imports', async () => {
    mockApiFetch.mockResolvedValue({ imported: 1, errors: [] })
    const { useImport } = await import('../useImport')
    const { uploadFile } = useImport()
    const file = new File(['content'], 'extrato.csv', { type: 'text/csv' })
    await uploadFile(file)
    expect(mockApiFetch).toHaveBeenCalledWith(
      '/api/v1/imports',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('sets isLoading to false after successful upload', async () => {
    mockApiFetch.mockResolvedValue({ imported: 1, errors: [] })
    const { useImport } = await import('../useImport')
    const { isLoading, uploadFile } = useImport()
    const file = new File(['content'], 'extrato.csv', { type: 'text/csv' })
    await uploadFile(file)
    expect(isLoading.value).toBe(false)
  })

  it('sets error and isLoading=false on API failure', async () => {
    mockApiFetch.mockRejectedValue(new Error('network error'))
    const { useImport } = await import('../useImport')
    const { error, isLoading, uploadFile } = useImport()
    const file = new File(['content'], 'extrato.csv', { type: 'text/csv' })
    await uploadFile(file)
    expect(error.value).toBeTruthy()
    expect(isLoading.value).toBe(false)
  })

  it('reset clears result and error', async () => {
    mockApiFetch.mockResolvedValue({ imported: 2, errors: ['linha 3: valor inválido'] })
    const { useImport } = await import('../useImport')
    const { result, error, uploadFile, reset } = useImport()
    const file = new File(['content'], 'extrato.csv', { type: 'text/csv' })
    await uploadFile(file)
    reset()
    expect(result.value).toBeNull()
    expect(error.value).toBeNull()
  })
})
