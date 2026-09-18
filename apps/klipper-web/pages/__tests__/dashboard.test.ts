/**
 * FIN-004 — o hero do painel mede saídas contra entradas. Sem nenhuma entrada no
 * ciclo não existe base de cálculo, e a página calculava a razão inline com
 * fallback para 0, desenhando "dentro da faixa · 0% da renda" como se fosse gasto
 * medido. Agora usa pctOfIncome(), que devolve null sem base, e o hero mostra o
 * estado de ausência de dado em vez de uma barra zerada.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import type { VueWrapper } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import type { Transaction } from '~/composables/useTransactions'
import Dashboard from '../dashboard.vue'

const transactions = ref<Transaction[]>([])
const totalDebits = ref(0)
const totalCredits = ref(0)
const latestOccurredOn = ref<string | null>(null)

mockNuxtImport('useTransactions', () => () => ({
  transactions,
  totalDebits,
  totalCredits,
  fetchTransactions: vi.fn(),
  fetchLatestOccurredOn: vi.fn(async () => latestOccurredOn.value),
  isLoading: ref(false),
  error: ref(null),
}))

mockNuxtImport('useMembers', () => () => ({
  members: ref([]),
  fetchMembers: vi.fn(),
  error: ref(null),
}))

mockNuxtImport('useReports', () => () => ({
  naturezaSplit: ref(null),
  fetchNaturezaSplit: vi.fn(),
  debtRanking: ref(null),
  fetchDebtRanking: vi.fn(),
  reimbursementCoverage: ref(null),
  fetchReimbursementCoverage: vi.fn(),
  isLoading: ref(false),
  error: ref(null),
}))

mockNuxtImport('useCategories', () => () => ({
  categories: ref([]),
  fetchCategories: vi.fn(),
  error: ref(null),
}))

function debit(amount: string): Transaction {
  return {
    id: 1,
    amount,
    transaction_type: 'debit',
    category_id: null,
    occurred_on: '2026-09-10',
  } as unknown as Transaction
}

let wrapper: VueWrapper | null = null

describe('dashboard.vue — hero do resultado do mês', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    transactions.value = [debit('120.00')]
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('FIN-004: sem nenhuma entrada no ciclo, mostra ausência de base em vez de barra zerada', async () => {
    totalCredits.value = 0
    totalDebits.value = 120

    wrapper = await mountSuspended(Dashboard)

    expect(wrapper.find('[data-testid="readout-no-budget"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="readout-bar"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Dentro da faixa do ciclo')
  })

  it('FIN-004: com entradas no ciclo, desenha a barra na proporção das saídas', async () => {
    totalCredits.value = 1000
    totalDebits.value = 400

    wrapper = await mountSuspended(Dashboard)

    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.exists()).toBe(true)
    expect(bar.attributes('style')).toContain('width: 40%')
    expect(wrapper.find('[data-testid="readout-no-budget"]').exists()).toBe(false)
  })
})

/**
 * UR-1 — o painel busca só o mês corrente. Depois de importar um extrato de
 * jan–jun, em setembro ele dizia "nenhum lançamento" e o usuário concluiu que a
 * importação tinha falhado. Mês vazio e base vazia não são o mesmo estado.
 */
describe('dashboard.vue — estado vazio', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    transactions.value = []
    totalDebits.value = 0
    totalCredits.value = 0
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('sem nenhum lançamento na base, mantém a mensagem de mês vazio', async () => {
    latestOccurredOn.value = null

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.text()).toContain('Nenhum lançamento neste mês ainda.')
    expect(wrapper.find('a[href="/relatorios"]').exists()).toBe(false)
  })

  it('com histórico em outro mês, diz até quando vão os dados e oferece o caminho', async () => {
    latestOccurredOn.value = '2026-06-29'

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.text()).toContain('Seu histórico vai até 29/06/2026.')
    expect(wrapper.text()).not.toContain('Nenhum lançamento neste mês ainda.')
    expect(wrapper.find('a[href="/relatorios"]').exists()).toBe(true)
  })
})
