export interface Account {
  id: number
  name: string
  institution: string | null
  account_type: string
  // null antes de opening_balance_on: a conta ainda não existia (spec 02, C-4a)
  balance: string | null
  opening_balance?: string
  opening_balance_on?: string
  currency: string
  active: boolean
  created_at: string
  updated_at: string
  saldo_fatura_atual: string | null
  pagamento_minimo: string | null
  juros_rotativo_am: string | null
  juros_rotativo_aa: string | null
  iof_projetado: string | null
  saldo_atualizado_em: string | null
}

export interface BalanceHistoryEntry {
  id: number
  occurred_on: string
  description: string
  delta: string
  balance: string
}

export interface BalanceHistory {
  opening_balance: string
  closing_balance: string
  entries: BalanceHistoryEntry[]
}

export function useAccounts() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()
  const accounts = useState<Account[]>('accounts', () => [])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAccounts() {
    isLoading.value = true
    error.value = null
    try {
      accounts.value = await apiFetch<Account[]>('/api/v1/accounts')
    } catch {
      error.value = 'Erro ao carregar contas.'
    } finally {
      isLoading.value = false
    }
  }

  async function createAccount(payload: Partial<Account>) {
    const data = await apiFetch<Account>('/api/v1/accounts', {
      method: 'POST',
      body: payload,
    })
    accounts.value = [...accounts.value, data]
    addToast('Conta adicionada', 'ok')
    return data
  }

  async function updateAccount(id: number, payload: Partial<Account>) {
    const data = await apiFetch<Account>(`/api/v1/accounts/${id}`, {
      method: 'PATCH',
      body: payload,
    })
    accounts.value = accounts.value.map((a) => (a.id === id ? data : a))
    addToast('Conta atualizada', 'ok')
    return data
  }

  async function deleteAccount(id: number) {
    await apiFetch(`/api/v1/accounts/${id}`, { method: 'DELETE' })
    accounts.value = accounts.value.filter((a) => a.id !== id)
    addToast('Conta removida', 'ok')
  }

  async function fetchBalanceHistory(id: number, from?: string, to?: string) {
    return apiFetch<BalanceHistory>(`/api/v1/accounts/${id}/balance-history`, {
      query: { ...(from ? { from } : {}), ...(to ? { to } : {}) },
    })
  }

  const totalBalance = computed(() =>
    accounts.value.reduce((sum, a) => sum + (a.balance === null ? 0 : parseFloat(a.balance)), 0)
  )

  return { accounts, isLoading, error, fetchAccounts, createAccount, updateAccount, deleteAccount, fetchBalanceHistory, totalBalance }
}
