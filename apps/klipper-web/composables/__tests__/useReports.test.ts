import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const mockApiFetch = vi.fn()

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: { value: 'test-token' },
}))

function makeMonthly(overrides = {}) {
  return {
    year: 2026,
    month: 6,
    total_debits: 270.50,
    total_credits: 5000.00,
    net: 4729.50,
    by_category: [
      { category_id: 1, category_name: 'Alimentação', category_icon: null, total: 150.00, count: 1 },
      { category_id: null, category_name: 'Sem categoria', category_icon: null, total: 120.50, count: 1 },
    ],
    ...overrides,
  }
}

function makeNetWorth(overrides = {}) {
  return {
    accounts_total: 4500.50,
    investments_cost: 25000.00,
    net_worth: 29500.50,
    accounts: [
      { id: 1, name: 'Nubank', balance: 3000.00 },
      { id: 2, name: 'BTG', balance: 1500.50 },
    ],
    investments_by_type: [
      { investment_type: 'stock', total_cost: 15000.00 },
      { investment_type: 'fii', total_cost: 10000.00 },
    ],
    ...overrides,
  }
}

describe('useReports', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApiFetch.mockResolvedValue({})
  })

  describe('fetchMonthly', () => {
    it('populates monthly state with API response', async () => {
      const payload = makeMonthly()
      mockApiFetch.mockResolvedValue(payload)

      const { useReports } = await import('../useReports')
      const { monthly, fetchMonthly } = useReports()
      await fetchMonthly(2026, 6)

      expect(monthly.value?.total_debits).toBeCloseTo(270.50)
      expect(monthly.value?.net).toBeCloseTo(4729.50)
      expect(monthly.value?.by_category).toHaveLength(2)
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue(makeMonthly())
      const { useReports } = await import('../useReports')
      const { isLoading, fetchMonthly } = useReports()
      await fetchMonthly(2026, 6)
      expect(isLoading.value).toBe(false)
    })

    it('passes year and month as query params when provided', async () => {
      mockApiFetch.mockResolvedValue(makeMonthly())
      const { useReports } = await import('../useReports')
      const { fetchMonthly } = useReports()
      await fetchMonthly(2025, 3)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/monthly',
        expect.objectContaining({ query: { year: 2025, month: 3 } }),
      )
    })

    it('defaults to current year/month when no args provided', async () => {
      mockApiFetch.mockResolvedValue(makeMonthly())
      const now = new Date()
      const { useReports } = await import('../useReports')
      const { fetchMonthly } = useReports()
      await fetchMonthly()
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/monthly',
        expect.objectContaining({
          query: { year: now.getFullYear(), month: now.getMonth() + 1 },
        }),
      )
    })
  })

  describe('fetchNetWorth', () => {
    it('populates netWorth state with API response', async () => {
      const payload = makeNetWorth()
      mockApiFetch.mockResolvedValue(payload)
      const { useReports } = await import('../useReports')
      const { netWorth, fetchNetWorth } = useReports()
      await fetchNetWorth()
      expect(netWorth.value?.net_worth).toBeCloseTo(29500.50)
      expect(netWorth.value?.accounts).toHaveLength(2)
      expect(netWorth.value?.investments_by_type).toHaveLength(2)
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue(makeNetWorth())
      const { useReports } = await import('../useReports')
      const { isLoading, fetchNetWorth } = useReports()
      await fetchNetWorth()
      expect(isLoading.value).toBe(false)
    })
  })
})
