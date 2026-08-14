/**
 * useInvestments tests — foco no comportamento de loading/erro de
 * fetchInvestments/fetchPortfolio, que a página investimentos.vue agora exibe.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

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

describe('useInvestments', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockAddToast.mockReset()
  })

  describe('fetchInvestments', () => {
    it('populates investments state with API response', async () => {
      mockApiFetch.mockResolvedValue([{ id: 1, account_id: null, ticker: 'PETR4', name: 'Petrobras', investment_type: 'acao', quantity: '10', average_price: '30.00', currency: 'BRL' }])
      const { investments, fetchInvestments } = useInvestments()
      await fetchInvestments()
      expect(investments.value).toHaveLength(1)
    })

    it('sets isLoading to false and error on a failed fetch', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { isLoading, error, fetchInvestments } = useInvestments()
      await fetchInvestments()
      expect(isLoading.value).toBe(false)
      expect(error.value).toBe('Erro ao carregar investimentos.')
    })

    it('clears a previous error on a successful fetch', async () => {
      const { error, fetchInvestments } = useInvestments()
      mockApiFetch.mockRejectedValueOnce(new Error('network error'))
      await fetchInvestments()
      expect(error.value).toBe('Erro ao carregar investimentos.')

      mockApiFetch.mockResolvedValueOnce([])
      await fetchInvestments()
      expect(error.value).toBeNull()
    })
  })

  describe('fetchPortfolio', () => {
    it('populates portfolio state with API response', async () => {
      mockApiFetch.mockResolvedValue({ total_positions: 2, total_cost: 1000, by_type: [] })
      const { portfolio, fetchPortfolio } = useInvestments()
      await fetchPortfolio()
      expect(portfolio.value?.total_positions).toBe(2)
    })

    it('sets error on a failed fetch', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { error, fetchPortfolio } = useInvestments()
      await fetchPortfolio()
      expect(error.value).toBe('Erro ao carregar investimentos.')
    })
  })
})
