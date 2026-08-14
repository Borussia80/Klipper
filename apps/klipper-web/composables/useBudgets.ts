export interface Budget {
  id: number
  category_id: number
  amount_limit: string
  period_month: number
  period_year: number
}

export interface BudgetSummaryRow {
  budget_id: number
  category_id: number
  category_name: string
  category_icon: string
  natureza: 'fixo' | 'cartao_parcelamento' | 'variavel'
  amount_limit: number
  spent: number
  remaining: number
  pct_used: number
  recorrencia: 'rotineiro' | 'ocasional' | 'pontual'
  months_present: number
  months_total: number
}

export function useBudgets() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()
  const budgets = useState<Budget[]>('budgets', () => [])
  const summary = useState<BudgetSummaryRow[]>('budgets.summary', () => [])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchBudgets(year?: number, month?: number) {
    isLoading.value = true
    error.value = null
    try {
      budgets.value = await apiFetch<Budget[]>('/api/v1/budgets', {
        query: year && month ? { year, month } : {},
      })
    } catch {
      error.value = 'Erro ao carregar orçamentos.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSummary(year?: number, month?: number) {
    isLoading.value = true
    error.value = null
    const now = new Date()
    try {
      summary.value = await apiFetch<BudgetSummaryRow[]>('/api/v1/budgets/summary', {
        query: {
          year: year ?? now.getFullYear(),
          month: month ?? now.getMonth() + 1,
        },
      })
    } catch {
      error.value = 'Erro ao carregar orçamento.'
    } finally {
      isLoading.value = false
    }
  }

  async function createBudget(payload: Partial<Budget>) {
    const data = await apiFetch<Budget>('/api/v1/budgets', {
      method: 'POST',
      body: payload,
    })
    budgets.value = [...budgets.value, data]
    addToast('Orçamento criado', 'ok')
    return data
  }

  async function deleteBudget(id: number) {
    await apiFetch(`/api/v1/budgets/${id}`, { method: 'DELETE' })
    budgets.value = budgets.value.filter((b) => b.id !== id)
    addToast('Orçamento removido', 'ok')
  }

  return { budgets, summary, isLoading, error, fetchBudgets, fetchSummary, createBudget, deleteBudget }
}
