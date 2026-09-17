/**
 * relatorios.vue — ícone de categoria/conta/investimento usa UiAppIcon (Phosphor
 * SVG), não emoji cru. Regressão: os três `.cat-icon` interpolavam texto puro
 * ('📦' de fallback, '🏦' e '📈' fixos), então a tela mostrava emoji solto em
 * vez do sistema de ícones do resto do app.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import type { VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import Relatorios from '../relatorios.vue'

const mockFetchMonthly = vi.fn()
const mockFetchNetWorth = vi.fn()
const mockFetchNetWorthHistory = vi.fn()
const mockFetchMembers = vi.fn()

const monthly = ref({
  year: 2026,
  month: 8,
  total_debits: 80,
  total_credits: 200,
  net: 120,
  by_category: [
    { category_id: 1, category_name: 'Mercado', category_icon: 'shopping', total: 50, count: 1 },
    { category_id: null, category_name: 'Sem categoria', category_icon: null, total: 30, count: 1 },
  ],
})

mockNuxtImport('useReports', () => () => ({
  monthly,
  netWorth: ref(null),
  netWorthHistory: ref(null),
  isLoading: ref(false),
  fetchMonthly: mockFetchMonthly,
  fetchNetWorth: mockFetchNetWorth,
  fetchNetWorthHistory: mockFetchNetWorthHistory,
}))

mockNuxtImport('useMembers', () => () => ({
  members: ref([]),
  fetchMembers: mockFetchMembers,
}))

let wrapper: VueWrapper | null = null

describe('relatorios.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('renderiza os ícones de categoria via UiAppIcon (SVG), sem emoji cru no DOM', async () => {
    wrapper = await mountSuspended(Relatorios)

    const catIcons = wrapper.findAll('.cat-icon')
    expect(catIcons).toHaveLength(2)
    catIcons.forEach((icon) => {
      expect(icon.find('svg').exists()).toBe(true)
    })

    expect(wrapper.text()).not.toMatch(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u)
  })

  it('usa o ícone "budget" como fallback quando a categoria não tem ícone', async () => {
    wrapper = await mountSuspended(Relatorios)

    const semCategoria = wrapper.findAll('.cat-row').at(1)!
    expect(semCategoria.text()).toContain('Sem categoria')
    expect(semCategoria.find('.cat-icon svg').exists()).toBe(true)
  })

  // ARCH-012: o estado do mock aqui é exatamente o da falha — netWorth nulo com
  // isLoading já false. Acontece de dois jeitos no app real: outro fetch paralelo
  // terminou primeiro e derrubou o loading, ou este fetch falhou e o ref ficou
  // nulo. Antes, o `?? 0` do template transformava os dois casos em R$ 0,00, um
  // patrimônio líquido de zero reais indistinguível de um de verdade.
  it('mostra "—" no patrimônio, não R$ 0,00, quando o dado não chegou', async () => {
    wrapper = await mountSuspended(Relatorios)
    await wrapper.findAll('.tab-btn').at(1)!.trigger('click')

    expect(wrapper.find('.nw-hero').text()).toContain('—')
    expect(wrapper.find('.nw-hero').text()).not.toContain('R$')
    expect(wrapper.text()).not.toContain('R$ 0,00')
  })
})
