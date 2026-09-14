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
 * A API recorta `GET /transactions` em páginas. Nenhuma tela do app
 * exibe um recorte — a lista alimenta filtros e somas locais — então buscamos
 * até esgotar as páginas. Parar antes faria as somas mostrarem um parcial sem
 * erro visível. 200 é o teto que o servidor aceita: menos páginas, menos idas.
 */
const PER_PAGE = 200

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
      let page = 1
      let totalPages = 1

      do {
        const res = await apiFetch.raw<Transaction[]>('/api/v1/transactions', {
          query: { ...filters, page, per_page: PER_PAGE },
        })
        const batch = res._data ?? []
        all.push(...batch)
        // header ausente (API ainda sem paginação) conta como página única
        totalPages = Number(res.headers.get('X-Total-Pages')) || 1
        if (!batch.length) break
        page += 1
      } while (page <= totalPages)

      transactions.value = all
    } catch {
      error.value = 'Erro ao carregar lançamentos.'
    } finally {
      isLoading.value = false
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
    createTransaction,
    updateTransaction,
    deleteTransaction,
    totalDebits,
    totalCredits,
  }
}
