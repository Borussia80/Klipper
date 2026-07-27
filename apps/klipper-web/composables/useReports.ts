export interface CategorySpending {
  category_id: number | null
  category_name: string
  category_icon: string | null
  total: number
  count: number
}

export interface MonthlyReport {
  year: number
  month: number
  total_debits: number
  total_credits: number
  net: number
  by_category: CategorySpending[]
}

export interface NetWorthReport {
  accounts_total: number
  investments_cost: number
  net_worth: number
  accounts: { id: number; name: string; balance: number }[]
  investments_by_type: { investment_type: string; total_cost: number }[]
}

export interface NaturezaSplitRow {
  natureza: 'fixo' | 'cartao_parcelamento' | 'variavel'
  total: number
  pct: number
}

export interface NaturezaSplitReport {
  year: number
  month: number
  total: number
  by_natureza: NaturezaSplitRow[]
}

export interface ReimbursementCoverageRow {
  category_id: number
  category_name: string
  category_icon: string | null
  reimbursed_by_category_name: string
  spent: number
  reimbursed: number
  coverage_pct: number | null
  historical_avg_pct: number | null
  months_considered: number
  alert: boolean
}

export interface ReimbursementCoverageReport {
  year: number
  month: number
  categories: ReimbursementCoverageRow[]
}

export interface DebtRankingRow {
  account_id: number
  name: string
  institution: string | null
  saldo_fatura_atual: number
  pagamento_minimo: number | null
  juros_rotativo_am: number
  juros_rotativo_aa: number | null
  iof_projetado: number | null
  encargos: number
  saldo_projetado_proximo_mes: number
  saldo_atualizado_em: string | null
}

export interface DebtRankingReport {
  cards: DebtRankingRow[]
}

export function useReports() {
  const { apiFetch } = useApi()
  const monthly = ref<MonthlyReport | null>(null)
  const netWorth = ref<NetWorthReport | null>(null)
  const naturezaSplit = ref<NaturezaSplitReport | null>(null)
  const reimbursementCoverage = ref<ReimbursementCoverageReport | null>(null)
  const debtRanking = ref<DebtRankingReport | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMonthly(year?: number, month?: number, memberId?: number) {
    isLoading.value = true
    error.value = null
    try {
      const now = new Date()
      monthly.value = await apiFetch<MonthlyReport>('/api/v1/reports/monthly', {
        query: {
          year: year ?? now.getFullYear(),
          month: month ?? now.getMonth() + 1,
          member_id: memberId,
        },
      })
    } catch {
      error.value = 'Erro ao carregar relatório mensal.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchNetWorth() {
    isLoading.value = true
    error.value = null
    try {
      netWorth.value = await apiFetch<NetWorthReport>('/api/v1/reports/net_worth')
    } catch {
      error.value = 'Erro ao carregar patrimônio.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchNaturezaSplit(year?: number, month?: number, memberId?: number) {
    isLoading.value = true
    error.value = null
    try {
      const now = new Date()
      naturezaSplit.value = await apiFetch<NaturezaSplitReport>('/api/v1/reports/natureza_split', {
        query: {
          year: year ?? now.getFullYear(),
          month: month ?? now.getMonth() + 1,
          member_id: memberId,
        },
      })
    } catch {
      error.value = 'Erro ao carregar composição de gastos.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchReimbursementCoverage(year?: number, month?: number, categoryId?: number) {
    isLoading.value = true
    error.value = null
    try {
      const now = new Date()
      reimbursementCoverage.value = await apiFetch<ReimbursementCoverageReport>('/api/v1/reports/reimbursement_coverage', {
        query: {
          year: year ?? now.getFullYear(),
          month: month ?? now.getMonth() + 1,
          category_id: categoryId,
        },
      })
    } catch {
      error.value = 'Erro ao carregar cobertura de reembolso.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDebtRanking() {
    isLoading.value = true
    error.value = null
    try {
      debtRanking.value = await apiFetch<DebtRankingReport>('/api/v1/reports/debt_ranking')
    } catch {
      error.value = 'Erro ao carregar prioridade de quitação.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    monthly,
    netWorth,
    naturezaSplit,
    reimbursementCoverage,
    debtRanking,
    isLoading,
    error,
    fetchMonthly,
    fetchNetWorth,
    fetchNaturezaSplit,
    fetchReimbursementCoverage,
    fetchDebtRanking,
  }
}
