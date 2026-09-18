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
import type { MonthlySeriesPoint } from '~/composables/useReports'
import Dashboard from '../dashboard.vue'
import DataHealthBanner from '~/components/ui/DataHealthBanner.vue'

const transactions = ref<Transaction[]>([])
const totalDebits = ref(0)
const totalCredits = ref(0)
const latestOccurredOn = ref<string | null>(null)

const mockFetchTransactions = vi.fn(async (_filters?: Record<string, unknown>) => {})
const mockFetchNaturezaSplit = vi.fn()
const mockFetchMonthlySeries = vi.fn()
const monthlySeries = ref<{ points: MonthlySeriesPoint[] } | null>(null)
const mockFetchDataHealth = vi.fn()
const dataHealth = ref<{ transactions: number; uncategorized: number; without_account: number } | null>(null)
const mockFetchReimbursementCoverage = vi.fn()

mockNuxtImport('useTransactions', () => () => ({
  transactions,
  totalDebits,
  totalCredits,
  fetchTransactions: mockFetchTransactions,
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
  fetchNaturezaSplit: mockFetchNaturezaSplit,
  monthlySeries,
  fetchMonthlySeries: mockFetchMonthlySeries,
  dataHealth,
  fetchDataHealth: mockFetchDataHealth,
  debtRanking: ref(null),
  fetchDebtRanking: vi.fn(),
  reimbursementCoverage: ref(null),
  fetchReimbursementCoverage: mockFetchReimbursementCoverage,
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

/**
 * O painel abria sempre no mês do calendário. Com o extrato real do Roberto
 * (jan–jun/2026) isso significava, em setembro, uma tela sem nada: 345
 * lançamentos no banco e nenhum na frente dele. O mês mostrado passa a ser o
 * último com movimento, dito em voz alta para não parecer o mês atual.
 */
describe('dashboard.vue — mês mostrado segue o movimento', () => {
  let porMes: Record<string, Transaction[]> = {}

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-09-18T12:00:00'))
    transactions.value = []
    totalDebits.value = 0
    totalCredits.value = 0
    latestOccurredOn.value = '2026-06-29'
    porMes = { '2026-6': [debit('120.00')] }
    mockFetchTransactions.mockImplementation(async (filters) => {
      const { year, month } = (filters ?? {}) as { year: number; month: number }
      transactions.value = porMes[`${year}-${month}`] ?? []
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    mockFetchTransactions.mockImplementation(async () => {})
    wrapper?.unmount()
    wrapper = null
  })

  it('setembro vazio com histórico até junho: mostra junho e diz que é o último mês com movimento', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(mockFetchTransactions).toHaveBeenCalledWith(expect.objectContaining({ year: 2026, month: 9 }))
    expect(mockFetchTransactions).toHaveBeenCalledWith(expect.objectContaining({ year: 2026, month: 6 }))

    const aviso = wrapper.find('[data-testid="mes-fallback"]')
    expect(aviso.exists()).toBe(true)
    expect(aviso.text()).toContain('Junho 2026')
    expect(wrapper.text()).not.toContain('Nenhum lançamento')
  })

  it('os relatórios do mês seguem o mês mostrado, não o do calendário', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(mockFetchNaturezaSplit).toHaveBeenLastCalledWith(2026, 6, undefined)
    expect(mockFetchReimbursementCoverage).toHaveBeenLastCalledWith(2026, 6)
  })

  it('com lançamentos no mês corrente, não volta no tempo', async () => {
    porMes = { '2026-9': [debit('50.00')] }

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.find('[data-testid="mes-fallback"]').exists()).toBe(false)
    expect(mockFetchTransactions).toHaveBeenCalledTimes(1)
    expect(mockFetchNaturezaSplit).toHaveBeenLastCalledWith(2026, 9, undefined)
  })

  it('base inteira vazia: segue na tela vazia, sem inventar mês', async () => {
    porMes = {}
    latestOccurredOn.value = null

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.find('[data-testid="mes-fallback"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Nenhum lançamento neste mês ainda.')
  })
})

/**
 * A série mensal responde a pergunta que vem depois de "quanto neste mês":
 * estou melhorando ou piorando? Ela termina no mês mostrado — se o painel
 * recuou para junho, a janela é jan–jun, não abr–set.
 */
describe('dashboard.vue — série mensal', () => {
  const pontos: MonthlySeriesPoint[] = [
    { year: 2026, month: 1, total_credits: 4000, total_debits: 3000, net: 1000 },
    { year: 2026, month: 2, total_credits: 0, total_debits: 0, net: 0 },
    { year: 2026, month: 3, total_credits: 4000, total_debits: 5000, net: -1000 },
    { year: 2026, month: 4, total_credits: 4000, total_debits: 2000, net: 2000 },
    { year: 2026, month: 5, total_credits: 0, total_debits: 999, net: -999 },
    { year: 2026, month: 6, total_credits: 5000, total_debits: 2500, net: 2500 },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-09-18T12:00:00'))
    transactions.value = [debit('120.00')]
    totalDebits.value = 120
    totalCredits.value = 0
    latestOccurredOn.value = null
    monthlySeries.value = { points: pontos }
  })

  afterEach(() => {
    vi.useRealTimers()
    monthlySeries.value = null
    wrapper?.unmount()
    wrapper = null
  })

  it('pede a janela de seis meses terminando no mês mostrado', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(mockFetchMonthlySeries).toHaveBeenLastCalledWith(2026, 9, 6, undefined)
  })

  it('desenha uma coluna por mês da janela', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.findAll('[data-testid="fluxo-mes"]')).toHaveLength(6)
  })

  it('sem série carregada, não desenha o bloco', async () => {
    monthlySeries.value = null

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.find('[data-testid="fluxo-mes"]').exists()).toBe(false)
  })
})

/**
 * A faixa de categorização fica acima do painel porque explica o painel: sem
 * categoria, os blocos que dependem dela ficam vazios.
 */
describe('dashboard.vue — faixa de categorização', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    transactions.value = [debit('120.00')]
    totalDebits.value = 120
    totalCredits.value = 0
    latestOccurredOn.value = null
    dataHealth.value = { transactions: 345, uncategorized: 338, without_account: 345 }
  })

  afterEach(() => {
    dataHealth.value = null
    wrapper?.unmount()
    wrapper = null
  })

  it('pede a contagem ao montar e mostra a faixa', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(mockFetchDataHealth).toHaveBeenCalled()
    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('338 de 345')
  })

  // A faixa aparece antes do estado vazio: quando o mês está sem lançamento, ela
  // continua sendo a explicação de por que as outras telas estão vazias.
  // Ligar os lançamentos à conta muda o saldo e muda a própria faixa: o painel
  // recarrega em vez de mostrar o estado anterior até o próximo F5.
  it('recarrega a contagem e o mês depois de ligar os lançamentos à conta', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()
    mockFetchDataHealth.mockClear()
    mockFetchTransactions.mockClear()

    wrapper.findComponent(DataHealthBanner).vm.$emit('corrigido')
    await flushPromises()

    expect(mockFetchDataHealth).toHaveBeenCalled()
    expect(mockFetchTransactions).toHaveBeenCalled()
  })

  it('aparece mesmo com o mês sem lançamento', async () => {
    transactions.value = []
    totalDebits.value = 0

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(true)
  })
})

/**
 * Densidade do mockup v2: o hero deixa de descrever o mês em prosa e passa a
 * mostrar entradas e saídas como dois números em mono, com a régua de ritmo
 * logo abaixo — 80% da renda gasta no dia 10 é outra história que no dia 28.
 */
describe('dashboard.vue — densidade do hero', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-09-18T12:00:00'))
    transactions.value = [debit('120.00')]
    totalCredits.value = 5000
    totalDebits.value = 2500
    latestOccurredOn.value = null
  })

  afterEach(() => {
    vi.useRealTimers()
    wrapper?.unmount()
    wrapper = null
  })

  it('mostra entradas e saídas como dois números, não como frase', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    const legs = wrapper.findAll('[data-testid="readout-leg"]')
    expect(legs).toHaveLength(2)
    expect(legs[0]!.text()).toContain('Entradas')
    expect(legs[1]!.text()).toContain('Saídas')
    expect(wrapper.text()).not.toContain('em entradas contra')
  })

  it('no mês corrente, mostra quanto do mês já passou', async () => {
    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.find('[data-testid="ritmo-dia"]').text()).toBe('dia 18 de 30')
  })

  it('quando o painel recuou, o mês está fechado e não tem ritmo a medir', async () => {
    transactions.value = []
    latestOccurredOn.value = '2026-06-29'
    mockFetchTransactions.mockImplementation(async (filters) => {
      const { month } = (filters ?? {}) as { month: number }
      transactions.value = month === 6 ? [debit('120.00')] : []
    })

    wrapper = await mountSuspended(Dashboard)
    await flushPromises()

    expect(wrapper.find('[data-testid="ritmo-fechado"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="ritmo-dia"]').exists()).toBe(false)
    mockFetchTransactions.mockImplementation(async () => {})
  })
})
