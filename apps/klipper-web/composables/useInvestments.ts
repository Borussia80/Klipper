export interface Investment {
  id: number
  account_id: number | null
  ticker: string | null
  name: string
  investment_type: string
  quantity: string
  average_price: string
  currency: string
}

export interface PortfolioAllocation {
  investment_type: string
  count: number
  total_cost: number
  pct_of_portfolio: number
}

export interface PortfolioTotals {
  total_positions: number
  total_cost: number
  by_type: PortfolioAllocation[]
}

export function useInvestments() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()
  const investments = useState<Investment[]>('investments', () => [])
  const portfolio = useState<PortfolioTotals | null>('investments.portfolio', () => null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchInvestments(type?: string) {
    isLoading.value = true
    error.value = null
    try {
      investments.value = await apiFetch<Investment[]>('/api/v1/investments', {
        query: type ? { type } : {},
      })
    } catch {
      error.value = 'Erro ao carregar investimentos.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPortfolio() {
    try {
      portfolio.value = await apiFetch<PortfolioTotals>('/api/v1/investments/portfolio')
    } catch {
      error.value = 'Erro ao carregar investimentos.'
    }
  }

  async function createInvestment(payload: Partial<Investment>) {
    const data = await apiFetch<Investment>('/api/v1/investments', {
      method: 'POST',
      body: payload,
    })
    investments.value = [...investments.value, data]
    addToast('Investimento adicionado', 'ok')
    return data
  }

  async function updateInvestment(id: number, payload: Partial<Investment>) {
    const data = await apiFetch<Investment>(`/api/v1/investments/${id}`, {
      method: 'PATCH',
      body: payload,
    })
    investments.value = investments.value.map((i) => (i.id === id ? data : i))
    addToast('Investimento atualizado', 'ok')
    return data
  }

  async function deleteInvestment(id: number) {
    await apiFetch(`/api/v1/investments/${id}`, { method: 'DELETE' })
    investments.value = investments.value.filter((i) => i.id !== id)
    addToast('Investimento removido', 'ok')
  }

  return {
    investments,
    portfolio,
    isLoading,
    error,
    fetchInvestments,
    fetchPortfolio,
    createInvestment,
    updateInvestment,
    deleteInvestment,
  }
}
