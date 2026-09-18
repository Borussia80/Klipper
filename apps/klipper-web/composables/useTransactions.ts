export interface Transaction {
  id: number
  account_id: number
  category_id: number | null
  description: string
  amount: string
  transaction_type: 'debit' | 'credit' | 'transfer'
  occurred_on: string
  notes: string | null
  installment_total: number | null
  installment_number: number | null
  member_id: number | null
}

export interface TransactionFilters {
  year?: number
  month?: number
  account_id?: number
  member_id?: number
  type?: string
}

/**
 * A API recorta `GET /transactions` por cursor. A lista alimenta filtros e
 * somas locais, então buscamos até esgotar os cursores para não exibir um
 * parcial sem erro visível.
 */
const PER_PAGE = 50

export function useTransactions() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()
  const transactions = useState<Transaction[]>('transactions', () => [])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTransactions(filters: TransactionFilters = {}) {
    isLoading.value = true
    error.value = null
    try {
      const all: Transaction[] = []
      let cursor: string | undefined

      do {
        const res = await apiFetch.raw<Transaction[]>('/api/v1/transactions', {
          query: { ...filters, per_page: PER_PAGE, ...(cursor ? { cursor } : {}) },
        })
        const batch = res._data ?? []
        all.push(...batch)
        if (!batch.length) break
        cursor = res.headers.get('X-Next-Cursor') || undefined
      } while (cursor)

      transactions.value = all
    } catch {
      error.value = 'Erro ao carregar lançamentos.'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Data do lançamento mais recente do usuário, ignorando o recorte de mês.
   * O painel só busca o mês corrente, então um mês vazio é indistinguível de
   * uma base vazia — e depois de importar meio ano de extrato o usuário lia
   * "nenhum lançamento" e concluía que a importação falhou (UR-1). Uma linha
   * basta para responder: `index` já ordena por occurred_on desc.
   */
  async function fetchLatestOccurredOn(filters: TransactionFilters = {}): Promise<string | null> {
    try {
      const rows = await apiFetch<Transaction[]>('/api/v1/transactions', {
        query: { ...filters, per_page: 1 },
      })
      return rows[0]?.occurred_on ?? null
    } catch {
      return null
    }
  }

  async function createTransaction(payload: Partial<Transaction>) {
    const data = await apiFetch<Transaction>('/api/v1/transactions', {
      method: 'POST',
      body: payload,
    })
    transactions.value = [data, ...transactions.value]
    addToast('Lançamento registrado', 'ok')
    return data
  }

  async function updateTransaction(id: number, payload: Partial<Transaction>) {
    const data = await apiFetch<Transaction>(`/api/v1/transactions/${id}`, {
      method: 'PATCH',
      body: payload,
    })
    transactions.value = transactions.value.map((t) => (t.id === id ? data : t))
    addToast('Lançamento atualizado', 'ok')
    return data
  }

  async function deleteTransaction(id: number, options: { silent?: boolean } = {}) {
    await apiFetch(`/api/v1/transactions/${id}`, { method: 'DELETE' })
    transactions.value = transactions.value.filter((t) => t.id !== id)
    if (!options.silent) addToast('Lançamento removido', 'ok')
  }

  const totalDebits = computed(() =>
    transactions.value
      .filter((t) => t.transaction_type === 'debit')
      .reduce((s, t) => s + parseFloat(t.amount), 0)
  )
  const totalCredits = computed(() =>
    transactions.value
      .filter((t) => t.transaction_type === 'credit')
      .reduce((s, t) => s + parseFloat(t.amount), 0)
  )

  return {
    transactions,
    isLoading,
    error,
    fetchTransactions,
    fetchLatestOccurredOn,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    totalDebits,
    totalCredits,
  }
}
