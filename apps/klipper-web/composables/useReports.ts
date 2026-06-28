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

export function useReports() {
  const { apiFetch } = useApi()
  const monthly = ref<MonthlyReport | null>(null)
  const netWorth = ref<NetWorthReport | null>(null)
  const isLoading = ref(false)

  async function fetchMonthly(year?: number, month?: number) {
    isLoading.value = true
    try {
      const now = new Date()
      monthly.value = await apiFetch<MonthlyReport>('/api/v1/reports/monthly', {
        query: {
          year: year ?? now.getFullYear(),
          month: month ?? now.getMonth() + 1,
        },
      })
    } finally {
      isLoading.value = false
    }
  }

  async function fetchNetWorth() {
    isLoading.value = true
    try {
      netWorth.value = await apiFetch<NetWorthReport>('/api/v1/reports/net_worth')
    } finally {
      isLoading.value = false
    }
  }

  return { monthly, netWorth, isLoading, fetchMonthly, fetchNetWorth }
}
