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

function makeNaturezaSplit(overrides = {}) {
  return {
    year: 2026,
    month: 6,
    total: 300.00,
    by_natureza: [
      { natureza: 'fixo', total: 150.00, pct: 50.0 },
      { natureza: 'cartao_parcelamento', total: 90.00, pct: 30.0 },
      { natureza: 'variavel', total: 60.00, pct: 20.0 },
    ],
    ...overrides,
  }
}

function makeReimbursementCoverage(overrides = {}) {
  return {
    year: 2026,
    month: 7,
    categories: [
      {
        category_id: 1,
        category_name: 'Terapia Pedro',
        category_icon: 'health',
        reimbursed_by_category_name: 'Reembolso Bradesco',
        spent: 400.00,
        reimbursed: 300.00,
        coverage_pct: 75.0,
        historical_avg_pct: 59.0,
        months_considered: 6,
        alert: false,
      },
    ],
    ...overrides,
  }
}

function makeDebtRanking(overrides = {}) {
  return {
    cards: [
      {
        account_id: 1,
        name: 'Itaú Personnalité',
        institution: 'Itaú',
        saldo_fatura_atual: 9603.90,
        pagamento_minimo: 960.39,
        juros_rotativo_am: 12.92,
        juros_rotativo_aa: 435.0,
        iof_projetado: 60.12,
        encargos: 1116.98,
        saldo_projetado_proximo_mes: 10781.00,
        saldo_atualizado_em: '2026-07-01T12:00:00Z',
      },
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

    it('passes member_id as a query param when provided', async () => {
      mockApiFetch.mockResolvedValue(makeMonthly())
      const { useReports } = await import('../useReports')
      const { fetchMonthly } = useReports()
      await fetchMonthly(2025, 3, 12)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/monthly',
        expect.objectContaining({ query: { year: 2025, month: 3, member_id: 12 } }),
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

  describe('fetchNaturezaSplit', () => {
    it('populates naturezaSplit state with API response', async () => {
      const payload = makeNaturezaSplit()
      mockApiFetch.mockResolvedValue(payload)

      const { useReports } = await import('../useReports')
      const { naturezaSplit, fetchNaturezaSplit } = useReports()
      await fetchNaturezaSplit(2026, 6)

      expect(naturezaSplit.value?.total).toBeCloseTo(300.00)
      expect(naturezaSplit.value?.by_natureza).toHaveLength(3)
      expect(naturezaSplit.value?.by_natureza[0].natureza).toBe('fixo')
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue(makeNaturezaSplit())
      const { useReports } = await import('../useReports')
      const { isLoading, fetchNaturezaSplit } = useReports()
      await fetchNaturezaSplit(2026, 6)
      expect(isLoading.value).toBe(false)
    })

    it('passes year and month as query params when provided', async () => {
      mockApiFetch.mockResolvedValue(makeNaturezaSplit())
      const { useReports } = await import('../useReports')
      const { fetchNaturezaSplit } = useReports()
      await fetchNaturezaSplit(2025, 3)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/natureza_split',
        expect.objectContaining({ query: { year: 2025, month: 3 } }),
      )
    })

    it('passes member_id as a query param when provided', async () => {
      mockApiFetch.mockResolvedValue(makeNaturezaSplit())
      const { useReports } = await import('../useReports')
      const { fetchNaturezaSplit } = useReports()
      await fetchNaturezaSplit(2025, 3, 12)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/natureza_split',
        expect.objectContaining({ query: { year: 2025, month: 3, member_id: 12 } }),
      )
    })

    it('defaults to current year/month when no args provided', async () => {
      mockApiFetch.mockResolvedValue(makeNaturezaSplit())
      const now = new Date()
      const { useReports } = await import('../useReports')
      const { fetchNaturezaSplit } = useReports()
      await fetchNaturezaSplit()
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/natureza_split',
        expect.objectContaining({
          query: { year: now.getFullYear(), month: now.getMonth() + 1 },
        }),
      )
    })
  })

  describe('fetchReimbursementCoverage', () => {
    it('populates reimbursementCoverage state with API response', async () => {
      const payload = makeReimbursementCoverage()
      mockApiFetch.mockResolvedValue(payload)

      const { useReports } = await import('../useReports')
      const { reimbursementCoverage, fetchReimbursementCoverage } = useReports()
      await fetchReimbursementCoverage(2026, 7)

      expect(reimbursementCoverage.value?.categories).toHaveLength(1)
      expect(reimbursementCoverage.value?.categories[0].category_name).toBe('Terapia Pedro')
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue(makeReimbursementCoverage())
      const { useReports } = await import('../useReports')
      const { isLoading, fetchReimbursementCoverage } = useReports()
      await fetchReimbursementCoverage(2026, 7)
      expect(isLoading.value).toBe(false)
    })

    it('passes year, month and category_id as query params when provided', async () => {
      mockApiFetch.mockResolvedValue(makeReimbursementCoverage())
      const { useReports } = await import('../useReports')
      const { fetchReimbursementCoverage } = useReports()
      await fetchReimbursementCoverage(2025, 3, 7)
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/reimbursement_coverage',
        expect.objectContaining({ query: { year: 2025, month: 3, category_id: 7 } }),
      )
    })

    it('defaults to current year/month when no args provided', async () => {
      mockApiFetch.mockResolvedValue(makeReimbursementCoverage())
      const now = new Date()
      const { useReports } = await import('../useReports')
      const { fetchReimbursementCoverage } = useReports()
      await fetchReimbursementCoverage()
      expect(mockApiFetch).toHaveBeenCalledWith(
        '/api/v1/reports/reimbursement_coverage',
        expect.objectContaining({
          query: { year: now.getFullYear(), month: now.getMonth() + 1, category_id: undefined },
        }),
      )
    })

    it('preserves null coverage_pct and true alert values without coercion', async () => {
      mockApiFetch.mockResolvedValue(makeReimbursementCoverage({
        categories: [
          {
            category_id: 2,
            category_name: 'Fisio',
            category_icon: null,
            reimbursed_by_category_name: 'Reembolso Convênio',
            spent: 0,
            reimbursed: 0,
            coverage_pct: null,
            historical_avg_pct: null,
            months_considered: 0,
            alert: true,
          },
        ],
      }))
      const { useReports } = await import('../useReports')
      const { reimbursementCoverage, fetchReimbursementCoverage } = useReports()
      await fetchReimbursementCoverage(2026, 7)

      const row = reimbursementCoverage.value?.categories[0]
      expect(row?.coverage_pct).toBeNull()
      expect(row?.alert).toBe(true)
    })
  })

  describe('fetchDebtRanking', () => {
    it('populates debtRanking state with API response', async () => {
      const payload = makeDebtRanking()
      mockApiFetch.mockResolvedValue(payload)

      const { useReports } = await import('../useReports')
      const { debtRanking, fetchDebtRanking } = useReports()
      await fetchDebtRanking()

      expect(debtRanking.value?.cards).toHaveLength(1)
      expect(debtRanking.value?.cards[0].encargos).toBeCloseTo(1116.98)
      expect(debtRanking.value?.cards[0].saldo_projetado_proximo_mes).toBeCloseTo(10781.00)
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue(makeDebtRanking())
      const { useReports } = await import('../useReports')
      const { isLoading, fetchDebtRanking } = useReports()
      await fetchDebtRanking()
      expect(isLoading.value).toBe(false)
    })

    it('calls the debt_ranking endpoint with no query params', async () => {
      mockApiFetch.mockResolvedValue(makeDebtRanking())
      const { useReports } = await import('../useReports')
      const { fetchDebtRanking } = useReports()
      await fetchDebtRanking()
      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/reports/debt_ranking')
    })

    it('preserves null pagamento_minimo and iof_projetado without coercion', async () => {
      mockApiFetch.mockResolvedValue(makeDebtRanking({
        cards: [
          {
            account_id: 2,
            name: 'Cartão sem dados completos',
            institution: null,
            saldo_fatura_atual: 500.00,
            pagamento_minimo: null,
            juros_rotativo_am: 10.0,
            juros_rotativo_aa: null,
            iof_projetado: null,
            encargos: 50.00,
            saldo_projetado_proximo_mes: 550.00,
            saldo_atualizado_em: null,
          },
        ],
      }))
      const { useReports } = await import('../useReports')
      const { debtRanking, fetchDebtRanking } = useReports()
      await fetchDebtRanking()

      const row = debtRanking.value?.cards[0]
      expect(row?.pagamento_minimo).toBeNull()
      expect(row?.iof_projetado).toBeNull()
      expect(row?.saldo_atualizado_em).toBeNull()
    })
  })
})
