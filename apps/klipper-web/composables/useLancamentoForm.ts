import type { Transaction } from '~/composables/useTransactions'

export type LancamentoTipo = 'gasto' | 'receita' | 'transferencia'

export const TIPO_OPCOES: { value: LancamentoTipo; label: string }[] = [
  { value: 'gasto', label: 'Gasto' },
  { value: 'receita', label: 'Receita' },
  { value: 'transferencia', label: 'Transferência' },
]

export function txTypeToTipo(txType: Transaction['transaction_type']): LancamentoTipo {
  if (txType === 'credit') return 'receita'
  if (txType === 'transfer') return 'transferencia'
  return 'gasto'
}

function tipoToTxType(tipo: LancamentoTipo): Transaction['transaction_type'] {
  if (tipo === 'receita') return 'credit'
  if (tipo === 'transferencia') return 'transfer'
  return 'debit'
}

/**
 * Estado e validação compartilhados pelos modais de lançamento (Novo e Editar).
 * Centraliza aqui evita que os dois formulários divirjam silenciosamente —
 * foi assim que a limpeza de categoria parou de funcionar só na edição.
 */
export function useLancamentoForm() {
  const { accounts, fetchAccounts } = useAccounts()
  const { categories, fetchCategories } = useCategories()

  const isLoadingData = ref(true)
  onMounted(async () => {
    await Promise.all([fetchAccounts(), fetchCategories()])
    isLoadingData.value = false
  })

  const tipo = ref<LancamentoTipo>('gasto')
  const valor = ref('')
  const descricao = ref('')
  const categoria = ref<number | null>(null)
  const conta = ref<number | null>(null)
  const data = ref(todayISO())
  const error = ref<string | null>(null)

  function validate(): string | null {
    const v = parseBRLAmount(valor.value)
    if (v === null || v <= 0) return 'Informe um valor válido'
    if (!descricao.value.trim()) return 'Informe uma descrição'
    if (isFutureDate(data.value)) return 'A data não pode ser futura'
    return null
  }

  const isValid = computed(() => validate() === null)

  function buildPayload(): Partial<Transaction> {
    const amount = parseBRLAmount(valor.value)!
    return {
      account_id: conta.value ?? undefined,
      category_id: categoria.value,
      description: descricao.value.trim(),
      amount: String(amount),
      transaction_type: tipoToTxType(tipo.value),
      occurred_on: data.value,
    }
  }

  function fillFrom(transaction: Transaction) {
    tipo.value = txTypeToTipo(transaction.transaction_type)
    valor.value = Number(transaction.amount).toFixed(2).replace('.', ',')
    descricao.value = transaction.description
    categoria.value = transaction.category_id
    conta.value = transaction.account_id
    data.value = transaction.occurred_on
    error.value = null
  }

  return {
    accounts,
    categories,
    isLoadingData,
    tipoOpcoes: TIPO_OPCOES,
    tipo,
    valor,
    descricao,
    categoria,
    conta,
    data,
    error,
    validate,
    isValid,
    buildPayload,
    fillFrom,
  }
}
