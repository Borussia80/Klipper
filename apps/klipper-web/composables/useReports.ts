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

export interface NetWorthHistoryPoint {
  year: number
  month: number
  net_worth: number
}

export interface NetWorthHistoryReport {
  period: string
  points: NetWorthHistoryPoint[]
}

export interface DataHealthReport {
  transactions: number
  uncategorized: number
  without_account: number
}

export interface MonthlySeriesPoint {
  year: number
  month: number
  total_credits: number
  total_debits: number
  net: number
}

export interface MonthlySeriesReport {
  points: MonthlySeriesPoint[]
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
  const netWorthHistory = ref<NetWorthHistoryReport | null>(null)
  const monthlySeries = ref<MonthlySeriesReport | null>(null)
  const dataHealth = ref<DataHealthReport | null>(null)
  const naturezaSplit = ref<NaturezaSplitReport | null>(null)
  const reimbursementCoverage = ref<ReimbursementCoverageReport | null>(null)
  const debtRanking = ref<DebtRankingReport | null>(null)
  // Contador, não booleano: relatorios.vue e dashboard.vue disparam três fetches
  // em paralelo sobre a mesma instância, e com um booleano a primeira resposta a
  // chegar zerava o isLoading enquanto as outras duas ainda estavam em voo. Nesse
  // intervalo a tela já se considerava carregada e imprimia R$ 0,00 no lugar do
  // total que ainda não tinha chegado — número financeiro falso, não placeholder.
  // O contador só volta a zero quando o último fetch termina (ARCH-012).
  const pendingRequests = ref(0)
  const isLoading = computed(() => pendingRequests.value > 0)
  const error = ref<string | null>(null)

  async function fetchMonthly(year?: number, month?: number, memberId?: number) {
    pendingRequests.value++
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
      pendingRequests.value--
    }
  }

  async function fetchNetWorth() {
    pendingRequests.value++
    error.value = null
    try {
      netWorth.value = await apiFetch<NetWorthReport>('/api/v1/reports/net_worth')
    } catch {
      error.value = 'Erro ao carregar patrimônio.'
    } finally {
      pendingRequests.value--
    }
  }

  async function fetchNetWorthHistory(period?: '3m' | '6m' | '1a' | 'max') {
    pendingRequests.value++
    error.value = null
    try {
      netWorthHistory.value = await apiFetch<NetWorthHistoryReport>('/api/v1/reports/net_worth_history', {
        query: period && period !== 'max' ? { period } : {},
      })
    } catch {
      error.value = 'Erro ao carregar histórico de patrimônio.'
    } finally {
      pendingRequests.value--
    }
  }

  async function fetchDataHealth() {
    pendingRequests.value++
    error.value = null
    try {
      dataHealth.value = await apiFetch<DataHealthReport>('/api/v1/reports/data_health')
    } catch {
      error.value = 'Erro ao carregar a saúde dos dados.'
    } finally {
      pendingRequests.value--
    }
  }

  // A janela inteira vem em uma resposta só: o gráfico de tendência com seis
  // chamadas de fetchMonthly seriam seis idas ao servidor para desenhar uma linha.
  async function fetchMonthlySeries(year?: number, month?: number, months?: number, memberId?: number) {
    pendingRequests.value++
    error.value = null
    try {
      const now = new Date()
      monthlySeries.value = await apiFetch<MonthlySeriesReport>('/api/v1/reports/monthly_series', {
        query: {
          year: year ?? now.getFullYear(),
          month: month ?? now.getMonth() + 1,
          months: months,
          member_id: memberId,
        },
      })
    } catch {
      error.value = 'Erro ao carregar a série mensal.'
    } finally {
      pendingRequests.value--
    }
  }

  async function fetchNaturezaSplit(year?: number, month?: number, memberId?: number) {
    pendingRequests.value++
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
      pendingRequests.value--
    }
  }

  async function fetchReimbursementCoverage(year?: number, month?: number, categoryId?: number) {
    pendingRequests.value++
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
      pendingRequests.value--
    }
  }

  async function fetchDebtRanking() {
    pendingRequests.value++
    error.value = null
    try {
      debtRanking.value = await apiFetch<DebtRankingReport>('/api/v1/reports/debt_ranking')
    } catch {
      error.value = 'Erro ao carregar prioridade de quitação.'
    } finally {
      pendingRequests.value--
    }
  }

  return {
    monthly,
    netWorth,
    netWorthHistory,
    monthlySeries,
    dataHealth,
    naturezaSplit,
    reimbursementCoverage,
    debtRanking,
    isLoading,
    error,
    fetchMonthly,
    fetchNetWorth,
    fetchNetWorthHistory,
    fetchMonthlySeries,
    fetchDataHealth,
    fetchNaturezaSplit,
    fetchReimbursementCoverage,
    fetchDebtRanking,
  }
}
