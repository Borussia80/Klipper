import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const apiFetch = vi.fn()
const addToast = vi.fn()

mockNuxtImport('useApi', () => () => ({ apiFetch }))
mockNuxtImport('useToast', () => () => ({ addToast }))

describe('useTransfers', () => {
  beforeEach(() => vi.clearAllMocks())

  it('creates one atomic transfer through its dedicated endpoint', async () => {
    apiFetch.mockResolvedValue({ debit: { id: 1 }, credit: { id: 2 } })
    const { createTransfer } = useTransfers()

    await createTransfer({ source_account_id: 1, destination_account_id: 2, amount: '40', occurred_on: '2026-10-20', description: 'Reserva' })

    expect(apiFetch).toHaveBeenCalledWith('/api/v1/transfers', expect.objectContaining({ method: 'POST' }))
    expect(addToast).toHaveBeenCalledWith('Transferência registrada', 'ok')
  })
})
