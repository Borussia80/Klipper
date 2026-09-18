/**
 * useTransactions tests — verifies state management, computed aggregates,
 * and API integration with mocked dependencies.
 */
import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

// ── mock setup ──────────────────────────────────────────────────────────────

type AnyMock = Mock<(...args: unknown[]) => unknown>
const mockApiFetch = vi.fn() as unknown as AnyMock & { raw: AnyMock }
const mockAddToast = vi.fn()

/**
 * `fetchTransactions` precisa dos headers de paginação, então chama
 * `apiFetch.raw`. O duplê padrão reembala o retorno de `mockApiFetch` numa
 * resposta sem headers — exatamente o que uma API sem paginação devolveria —
 * para que os testes que só querem uma lista continuem mockando `mockApiFetch`.
 */
async function defaultRaw(...args: unknown[]) {
  return { _data: await mockApiFetch(...args), headers: new Headers() }
}
mockApiFetch.raw = vi.fn(defaultRaw)

function pagina(data: unknown, headers: Record<string, string> = {}) {
  return { _data: data, headers: new Headers(headers) }
}

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: { value: 'test-token' },
}))

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

// ── filterTransactions (pure helper tested independently) ────────────────────

type FilterType = 'all' | 'credit' | 'debit'

function filterTransactions<T extends { transaction_type: string }>(
  txns: T[],
  filter: FilterType,
): T[] {
  if (filter === 'all') return txns
  return txns.filter((t) => t.transaction_type === filter)
}

// ── helpers ─────────────────────────────────────────────────────────────────

function makeTx(overrides: Partial<{
  id: number
  account_id: number
  category_id: number | null
  description: string
  amount: string
  transaction_type: 'debit' | 'credit' | 'transfer'
  occurred_on: string
  notes: string | null
  installment_total: number | null
  installment_number: number | null
}> = {}) {
  return {
    id: 1,
    account_id: 1,
    category_id: null,
    description: 'Test transaction',
    amount: '100.00',
    transaction_type: 'debit' as const,
    occurred_on: '2026-06-01',
    notes: null,
    installment_total: null,
    installment_number: null,
    ...overrides,
  }
}

// ── tests ────────────────────────────────────────────────────────────────────

describe('useTransactions', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockApiFetch.raw.mockReset()
    mockApiFetch.raw.mockImplementation(defaultRaw)
    mockAddToast.mockReset()
  })

  // ── fetchTransactions ──────────────────────────────────────────────────────

  describe('fetchTransactions', () => {
    it('populates transactions state with API response', async () => {
      mockApiFetch.mockResolvedValue([
        makeTx({ id: 1, description: 'Supermercado' }),
        makeTx({ id: 2, description: 'Salário', transaction_type: 'credit' }),
      ])
      const { transactions, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(transactions.value).toHaveLength(2)
      expect(transactions.value[0].description).toBe('Supermercado')
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue([])
      const { isLoading, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(isLoading.value).toBe(false)
    })

    it('sets isLoading to false after a failed fetch', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { isLoading, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(isLoading.value).toBe(false)
    })

    it('sets error state on API failure', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { error, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(error.value).toBeTruthy()
    })

    it('accepts filter arguments (passes them to API)', async () => {
      mockApiFetch.mockResolvedValue([])
      const { fetchTransactions } = useTransactions()
      await fetchTransactions({ year: 2026, month: 6 })
      expect(mockApiFetch.raw).toHaveBeenCalledWith('/api/v1/transactions', {
        query: expect.objectContaining({ year: 2026, month: 6 }),
      })
    })
  })

  // ── paginação ──────────────────────────────────────────────────────────────

  describe('paginação por cursor', () => {
    it('concatena as páginas seguintes até esgotar', async () => {
      mockApiFetch.raw
        .mockResolvedValueOnce(pagina([makeTx({ id: 1 })], { 'X-Next-Cursor': 'cursor-1' }))
        .mockResolvedValueOnce(pagina([makeTx({ id: 2 })], { 'X-Next-Cursor': 'cursor-2' }))
        .mockResolvedValueOnce(pagina([makeTx({ id: 3 })]))

      const { transactions, fetchTransactions } = useTransactions()
      await fetchTransactions()

      expect(mockApiFetch.raw).toHaveBeenCalledTimes(3)
      expect(transactions.value.map((t) => t.id)).toEqual([1, 2, 3])
    })

    it('envia o cursor retornado pela página anterior', async () => {
      mockApiFetch.raw
        .mockResolvedValueOnce(pagina([makeTx({ id: 1 })], { 'X-Next-Cursor': 'cursor-1' }))
        .mockResolvedValueOnce(pagina([makeTx({ id: 2 })]))

      const { fetchTransactions } = useTransactions()
      await fetchTransactions()

      expect((mockApiFetch.raw.mock.calls[0][1] as { query: object }).query).not.toHaveProperty('cursor')
      expect((mockApiFetch.raw.mock.calls[1][1] as { query: { cursor: string } }).query.cursor).toBe('cursor-1')
    })

    it('faz uma só chamada quando tudo cabe na primeira página', async () => {
      mockApiFetch.raw.mockResolvedValueOnce(
        pagina([makeTx({ id: 1 })])
      )

      const { fetchTransactions } = useTransactions()
      await fetchTransactions()

      expect(mockApiFetch.raw).toHaveBeenCalledTimes(1)
    })

    it('para na primeira página se a API não anunciar paginação', async () => {
      mockApiFetch.raw.mockResolvedValue(pagina([makeTx({ id: 1 })]))

      const { transactions, fetchTransactions } = useTransactions()
      await fetchTransactions()

      expect(mockApiFetch.raw).toHaveBeenCalledTimes(1)
      expect(transactions.value).toHaveLength(1)
    })

    // O laço só termina por dado que vem da resposta; página vazia encerra
    // mesmo que o header prometa mais, senão um total errado gira sem fim.
    it('para numa página vazia mesmo se o cursor continuar presente', async () => {
      mockApiFetch.raw
        .mockResolvedValueOnce(pagina([makeTx({ id: 1 })], { 'X-Next-Cursor': 'cursor-1' }))
        .mockResolvedValueOnce(pagina([], { 'X-Next-Cursor': 'cursor-2' }))

      const { transactions, fetchTransactions } = useTransactions()
      await fetchTransactions()

      expect(mockApiFetch.raw).toHaveBeenCalledTimes(2)
      expect(transactions.value).toHaveLength(1)
    })

    it('mantém os filtros em todas as páginas', async () => {
      mockApiFetch.raw
        .mockResolvedValueOnce(pagina([makeTx({ id: 1 })], { 'X-Next-Cursor': 'cursor-1' }))
        .mockResolvedValueOnce(pagina([makeTx({ id: 2 })]))

      const { fetchTransactions } = useTransactions()
      await fetchTransactions({ year: 2026, month: 6 })

      for (const call of mockApiFetch.raw.mock.calls) {
        expect((call[1] as { query: object }).query).toMatchObject({ year: 2026, month: 6 })
      }
    })
  })

  // ── totalDebits ────────────────────────────────────────────────────────────

  describe('totalDebits', () => {
    it('sums only debit transactions', async () => {
      mockApiFetch.mockResolvedValue([
        makeTx({ id: 1, amount: '100.00', transaction_type: 'debit' }),
        makeTx({ id: 2, amount: '50.00', transaction_type: 'credit' }),
        makeTx({ id: 3, amount: '75.00', transaction_type: 'debit' }),
      ])
      const { totalDebits, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(totalDebits.value).toBeCloseTo(175.0)
    })

    it('returns 0 when there are no debit transactions', async () => {
      mockApiFetch.mockResolvedValue([
        makeTx({ id: 1, amount: '200.00', transaction_type: 'credit' }),
      ])
      const { totalDebits, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(totalDebits.value).toBe(0)
    })

    it('returns 0 when transactions list is empty', async () => {
      mockApiFetch.mockResolvedValue([])
      const { totalDebits, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(totalDebits.value).toBe(0)
    })
  })

  // ── totalCredits ───────────────────────────────────────────────────────────

  describe('totalCredits', () => {
    it('sums only credit transactions', async () => {
      mockApiFetch.mockResolvedValue([
        makeTx({ id: 1, amount: '3000.00', transaction_type: 'credit' }),
        makeTx({ id: 2, amount: '100.00', transaction_type: 'debit' }),
        makeTx({ id: 3, amount: '500.00', transaction_type: 'credit' }),
      ])
      const { totalCredits, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(totalCredits.value).toBeCloseTo(3500.0)
    })

    it('returns 0 when there are no credit transactions', async () => {
      mockApiFetch.mockResolvedValue([
        makeTx({ id: 1, amount: '100.00', transaction_type: 'debit' }),
      ])
      const { totalCredits, fetchTransactions } = useTransactions()
      await fetchTransactions()
      expect(totalCredits.value).toBe(0)
    })
  })

  // ── createTransaction ──────────────────────────────────────────────────────

  describe('createTransaction', () => {
    it('prepends the new transaction to the list', async () => {
      mockApiFetch.mockResolvedValueOnce([
        makeTx({ id: 1, description: 'Existing' }),
      ])
      const newTx = makeTx({ id: 99, description: 'New Entry' })
      mockApiFetch.mockResolvedValueOnce(newTx)

      const { transactions, fetchTransactions, createTransaction } = useTransactions()
      await fetchTransactions()
      await createTransaction({ description: 'New Entry', amount: '100.00', transaction_type: 'debit' })

      expect(transactions.value[0].id).toBe(99)
      expect(transactions.value[0].description).toBe('New Entry')
    })

    it('shows success toast after creation', async () => {
      const newTx = makeTx({ id: 10 })
      mockApiFetch.mockResolvedValue(newTx)

      const { createTransaction } = useTransactions()
      await createTransaction({ description: 'Gas', amount: '50.00', transaction_type: 'debit' })

      expect(mockAddToast).toHaveBeenCalledWith('Lançamento registrado', 'ok')
    })

    it('returns the created transaction', async () => {
      const newTx = makeTx({ id: 77, description: 'Pharmacy' })
      mockApiFetch.mockResolvedValue(newTx)

      const { createTransaction } = useTransactions()
      const result = await createTransaction({ description: 'Pharmacy' })
      expect(result.id).toBe(77)
    })
  })

  // ── updateTransaction ──────────────────────────────────────────────────────

  describe('updateTransaction', () => {
    it('replaces the matching transaction in state', async () => {
      mockApiFetch.mockResolvedValueOnce([makeTx({ id: 1, description: 'Old' })])
      const updated = makeTx({ id: 1, description: 'Updated' })
      mockApiFetch.mockResolvedValueOnce(updated)

      const { transactions, fetchTransactions, updateTransaction } = useTransactions()
      await fetchTransactions()
      await updateTransaction(1, { description: 'Updated' })

      expect(transactions.value[0].description).toBe('Updated')
    })

    it('shows success toast after update', async () => {
      mockApiFetch.mockResolvedValueOnce([makeTx({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(makeTx({ id: 1 }))

      const { fetchTransactions, updateTransaction } = useTransactions()
      await fetchTransactions()
      await updateTransaction(1, { description: 'Fixed' })

      expect(mockAddToast).toHaveBeenCalledWith('Lançamento atualizado', 'ok')
    })
  })

  // ── deleteTransaction ──────────────────────────────────────────────────────

  describe('deleteTransaction', () => {
    it('removes the transaction from state', async () => {
      mockApiFetch.mockResolvedValueOnce([
        makeTx({ id: 1, description: 'Keep' }),
        makeTx({ id: 2, description: 'Delete Me' }),
      ])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { transactions, fetchTransactions, deleteTransaction } = useTransactions()
      await fetchTransactions()
      await deleteTransaction(2)

      expect(transactions.value).toHaveLength(1)
      expect(transactions.value[0].id).toBe(1)
    })

    it('shows success toast after deletion', async () => {
      mockApiFetch.mockResolvedValueOnce([makeTx({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { fetchTransactions, deleteTransaction } = useTransactions()
      await fetchTransactions()
      await deleteTransaction(1)

      expect(mockAddToast).toHaveBeenCalledWith('Lançamento removido', 'ok')
    })
  })
})

describe('filterTransactions', () => {
  const txns = [
    { id: 1, transaction_type: 'credit', description: 'Salário', amount: '5000' },
    { id: 2, transaction_type: 'debit', description: 'Uber', amount: '25' },
    { id: 3, transaction_type: 'debit', description: 'Mercado', amount: '200' },
  ]

  it('retorna todas com filtro "all"', () => {
    expect(filterTransactions(txns, 'all')).toHaveLength(3)
  })

  it('retorna só créditos com filtro "credit"', () => {
    const result = filterTransactions(txns, 'credit')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe(1)
  })

  it('retorna só débitos com filtro "debit"', () => {
    const result = filterTransactions(txns, 'debit')
    expect(result).toHaveLength(2)
    expect(result.every((t) => t.transaction_type === 'debit')).toBe(true)
  })

  it('retorna array vazio se nenhuma transação bater', () => {
    expect(filterTransactions([], 'credit')).toHaveLength(0)
  })
  describe('assignAccountToOrphans', () => {
    it('envia a conta escolhida e devolve quantos lançamentos foram ligados', async () => {
      mockApiFetch.mockResolvedValue({ updated: 345 })

      const { useTransactions } = await import('../useTransactions')
      const { assignAccountToOrphans } = useTransactions()
      const updated = await assignAccountToOrphans(7)

      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/transactions/assign_account', {
        method: 'POST',
        body: { account_id: 7 },
      })
      expect(updated).toBe(345)
    })
  })

})
