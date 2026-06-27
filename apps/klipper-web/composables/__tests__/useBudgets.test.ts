/**
 * useBudgets tests — verifies state management for budget envelope logic.
 *
 * Mocks useApi and useToast so no real HTTP calls are made.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

// ── mock setup ──────────────────────────────────────────────────────────────

const mockApiFetch = vi.fn()
const mockAddToast = vi.fn()

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: { value: 'test-token' },
}))

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

// ── helpers ─────────────────────────────────────────────────────────────────

function makeBudget(overrides: Partial<{
  id: number
  category_id: number
  amount_limit: string
  period_month: number
  period_year: number
}> = {}) {
  return {
    id: 1,
    category_id: 1,
    amount_limit: '500.00',
    period_month: 6,
    period_year: 2026,
    ...overrides,
  }
}

function makeSummaryRow(overrides: Partial<{
  budget_id: number
  category_id: number
  category_name: string
  category_icon: string
  amount_limit: number
  spent: number
  remaining: number
  pct_used: number
}> = {}) {
  return {
    budget_id: 1,
    category_id: 1,
    category_name: 'Alimentação',
    category_icon: '🍔',
    amount_limit: 1000,
    spent: 400,
    remaining: 600,
    pct_used: 0.4,
    ...overrides,
  }
}

// ── tests ────────────────────────────────────────────────────────────────────

describe('useBudgets', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockAddToast.mockReset()
  })

  // ── fetchBudgets ───────────────────────────────────────────────────────────

  describe('fetchBudgets', () => {
    it('populates budgets state with API response', async () => {
      mockApiFetch.mockResolvedValue([
        makeBudget({ id: 1, category_id: 1 }),
        makeBudget({ id: 2, category_id: 2 }),
      ])
      const { budgets, fetchBudgets } = useBudgets()
      await fetchBudgets()
      expect(budgets.value).toHaveLength(2)
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue([])
      const { isLoading, fetchBudgets } = useBudgets()
      await fetchBudgets()
      expect(isLoading.value).toBe(false)
    })

    it('sets isLoading to false after a failed fetch', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { isLoading, fetchBudgets } = useBudgets()
      // useBudgets fetchBudgets uses try/finally but no catch — it will throw
      try { await fetchBudgets() } catch { /* expected */ }
      expect(isLoading.value).toBe(false)
    })

    it('passes year and month as query params when provided', async () => {
      mockApiFetch.mockResolvedValue([])
      const { fetchBudgets } = useBudgets()
      await fetchBudgets(2026, 6)
      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/budgets', {
        query: { year: 2026, month: 6 },
      })
    })

    it('passes empty query when year/month are omitted', async () => {
      mockApiFetch.mockResolvedValue([])
      const { fetchBudgets } = useBudgets()
      await fetchBudgets()
      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/budgets', {
        query: {},
      })
    })
  })

  // ── fetchSummary ───────────────────────────────────────────────────────────

  describe('fetchSummary', () => {
    it('populates summary state with API response', async () => {
      const rows = [
        makeSummaryRow({ budget_id: 1, category_name: 'Alimentação' }),
        makeSummaryRow({ budget_id: 2, category_name: 'Transporte' }),
      ]
      mockApiFetch.mockResolvedValue(rows)
      const { summary, fetchSummary } = useBudgets()
      await fetchSummary(2026, 6)
      expect(summary.value).toHaveLength(2)
      expect(summary.value[0].category_name).toBe('Alimentação')
    })

    it('exposes numeric budget fields correctly', async () => {
      mockApiFetch.mockResolvedValue([
        makeSummaryRow({ amount_limit: 1000, spent: 750, remaining: 250, pct_used: 0.75 }),
      ])
      const { summary, fetchSummary } = useBudgets()
      await fetchSummary(2026, 6)
      const row = summary.value[0]
      expect(row.amount_limit).toBe(1000)
      expect(row.spent).toBe(750)
      expect(row.remaining).toBe(250)
      expect(row.pct_used).toBeCloseTo(0.75)
    })

    it('defaults to current year/month when no args provided', async () => {
      mockApiFetch.mockResolvedValue([])
      const { fetchSummary } = useBudgets()
      await fetchSummary()

      const now = new Date()
      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/budgets/summary', {
        query: {
          year: now.getFullYear(),
          month: now.getMonth() + 1,
        },
      })
    })

    it('uses provided year and month when given', async () => {
      mockApiFetch.mockResolvedValue([])
      const { fetchSummary } = useBudgets()
      await fetchSummary(2025, 12)
      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/budgets/summary', {
        query: { year: 2025, month: 12 },
      })
    })

    it('sets summary to empty array when API returns none', async () => {
      mockApiFetch.mockResolvedValue([])
      const { summary, fetchSummary } = useBudgets()
      await fetchSummary(2026, 1)
      expect(summary.value).toHaveLength(0)
    })
  })

  // ── createBudget ───────────────────────────────────────────────────────────

  describe('createBudget', () => {
    it('appends the new budget to budgets state', async () => {
      mockApiFetch.mockResolvedValueOnce([]) // fetchBudgets baseline
      const newBudget = makeBudget({ id: 42, category_id: 5 })
      mockApiFetch.mockResolvedValueOnce(newBudget)

      const { budgets, fetchBudgets, createBudget } = useBudgets()
      await fetchBudgets()
      await createBudget({ category_id: 5, amount_limit: '300.00', period_month: 6, period_year: 2026 })

      expect(budgets.value.find((b) => b.id === 42)).toBeDefined()
    })

    it('shows success toast after creation', async () => {
      const newBudget = makeBudget({ id: 10 })
      mockApiFetch.mockResolvedValue(newBudget)

      const { createBudget } = useBudgets()
      await createBudget({ category_id: 1, amount_limit: '200.00', period_month: 6, period_year: 2026 })

      expect(mockAddToast).toHaveBeenCalledWith('Orçamento criado', 'ok')
    })

    it('returns the created budget', async () => {
      const newBudget = makeBudget({ id: 77 })
      mockApiFetch.mockResolvedValue(newBudget)

      const { createBudget } = useBudgets()
      const result = await createBudget({ category_id: 3 })
      expect(result.id).toBe(77)
    })
  })

  // ── deleteBudget ───────────────────────────────────────────────────────────

  describe('deleteBudget', () => {
    it('removes the budget from state', async () => {
      mockApiFetch.mockResolvedValueOnce([
        makeBudget({ id: 1 }),
        makeBudget({ id: 2 }),
      ])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { budgets, fetchBudgets, deleteBudget } = useBudgets()
      await fetchBudgets()
      await deleteBudget(2)

      expect(budgets.value).toHaveLength(1)
      expect(budgets.value[0].id).toBe(1)
    })

    it('shows success toast after deletion', async () => {
      mockApiFetch.mockResolvedValueOnce([makeBudget({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { fetchBudgets, deleteBudget } = useBudgets()
      await fetchBudgets()
      await deleteBudget(1)

      expect(mockAddToast).toHaveBeenCalledWith('Orçamento removido', 'ok')
    })
  })
})
