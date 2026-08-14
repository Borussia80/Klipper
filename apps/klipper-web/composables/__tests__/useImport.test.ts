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

  describe('previewFile', () => {
    const previewResponse = {
      adapter: 'itau_extrato',
      rows: [
        {
          occurred_on: '2026-06-25',
          description: 'JOAOEMARIA',
          amount: '-37.50',
          installment_number: null,
          installment_total: null,
          page: 1,
          metadata: {},
          suggested_member_id: null,
          token: 'signed-token-abc',
        },
      ],
      warnings: [],
    }

    it('sets preview state on successful PDF preview', async () => {
      mockApiFetch.mockResolvedValue(previewResponse)
      const { useImport } = await import('../useImport')
      const { preview, previewFile } = useImport()
      const file = new File(['content'], 'extrato.pdf', { type: 'application/pdf' })
      await previewFile(file)
      expect(preview.value?.adapter).toBe('itau_extrato')
      expect(preview.value?.rows).toHaveLength(1)
    })

    it('exposes suggested_member_id from the backend on preview rows', async () => {
      const withSuggestion = {
        ...previewResponse,
        rows: [ { ...previewResponse.rows[0], metadata: { cardholder: 'CLAREAANAALMEIDA (final 7445)' }, suggested_member_id: 12 } ],
      }
      mockApiFetch.mockResolvedValue(withSuggestion)
      const { useImport } = await import('../useImport')
      const { preview, previewFile } = useImport()
      const file = new File(['content'], 'fatura.pdf', { type: 'application/pdf' })
      await previewFile(file)
      expect(preview.value?.rows[0].suggested_member_id).toBe(12)
    })

    it('sends FormData with file to /api/v1/imports/preview', async () => {
      mockApiFetch.mockResolvedValue(previewResponse)
      const { useImport } = await import('../useImport')
      const { previewFile } = useImport()
      const file = new File(['content'], 'fatura.pdf', { type: 'application/pdf' })
      await previewFile(file)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/imports/preview',
        expect.objectContaining({ method: 'POST' }),
      )
    })

    it('sets error and isLoading=false when preview fails', async () => {
      mockApiFetch.mockRejectedValue(new Error('layout não reconhecido'))
      const { useImport } = await import('../useImport')
      const { error, isLoading, preview, previewFile } = useImport()
      const file = new File(['content'], 'estranho.pdf', { type: 'application/pdf' })
      await previewFile(file)
      expect(error.value).toBeTruthy()
      expect(isLoading.value).toBe(false)
      expect(preview.value).toBeNull()
    })
  })

  describe('confirmImport', () => {
    const rows = [
      {
        occurred_on: '2026-06-25',
        description: 'JOAOEMARIA',
        amount: '-37.50',
        installment_number: null,
        installment_total: null,
        page: 1,
        metadata: {},
        token: 'signed-token-abc',
      },
    ]

    it('sends rows and account_id to /api/v1/imports/confirm', async () => {
      mockApiFetch.mockResolvedValue({ imported: 1, errors: [] })
      const { useImport } = await import('../useImport')
      const { confirmImport } = useImport()
      await confirmImport(rows, 7)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/imports/confirm',
        expect.objectContaining({ method: 'POST', body: { rows, account_id: 7 } }),
      )
    })

    it('sets result and clears preview on success', async () => {
      mockApiFetch.mockResolvedValue({ imported: 1, errors: [] })
      const { useImport } = await import('../useImport')
      const { result, preview, previewFile, confirmImport } = useImport()
      await previewFile(new File(['content'], 'extrato.pdf', { type: 'application/pdf' }))
      await confirmImport(rows)
      expect(result.value?.imported).toBe(1)
      expect(preview.value).toBeNull()
    })

    it('sets error and isLoading=false on confirm failure', async () => {
      mockApiFetch.mockRejectedValue(new Error('erro ao confirmar'))
      const { useImport } = await import('../useImport')
      const { error, isLoading, confirmImport } = useImport()
      await confirmImport(rows)
      expect(error.value).toBeTruthy()
      expect(isLoading.value).toBe(false)
    })

    it('passes through a member_id set on a row to /api/v1/imports/confirm', async () => {
      mockApiFetch.mockResolvedValue({ imported: 1, errors: [] })
      const { useImport } = await import('../useImport')
      const { confirmImport } = useImport()
      const rowsWithMember = [ { ...rows[0], suggested_member_id: 12, member_id: 12 } ]
      await confirmImport(rowsWithMember, 7)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/imports/confirm',
        expect.objectContaining({ method: 'POST', body: { rows: rowsWithMember, account_id: 7 } }),
      )
    })

    it('SEC-17: keeps the signed token intact when member_id is set on a row', async () => {
      const { confirmImport } = useImport()
      const rowsWithMember = [ { ...rows[0], member_id: 12 } ]
      await confirmImport(rowsWithMember, 7)

      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/imports/confirm',
        expect.objectContaining({
          body: expect.objectContaining({ rows: [ expect.objectContaining({ token: 'signed-token-abc' }) ] }),
        }),
      )
    })
  })
})
