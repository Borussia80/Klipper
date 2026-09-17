/**
 * FIN-007 — pct_of_portfolio chega null quando o custo líquido da carteira é zero
 * ou negativo, porque porcentagem sobre base zero não existe. Antes o back mandava
 * 0,0% para todos os tipos e esta tela desenhava a barra de alocação com larguras
 * zeradas e escrevia "0%" na legenda, como se fosse alocação medida. Com o null,
 * sem o tratamento desta tela, a legenda passaria a escrever "null%".
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import type { VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import type { PortfolioTotals } from '~/composables/useInvestments'
import Investimentos from '../investimentos.vue'

const portfolio = ref<PortfolioTotals | null>(null)
const mockFetchInvestments = vi.fn()
const mockFetchPortfolio = vi.fn()

mockNuxtImport('useInvestments', () => () => ({
  investments: ref([]),
  portfolio,
  isLoading: ref(false),
  error: ref(null),
  fetchInvestments: mockFetchInvestments,
  fetchPortfolio: mockFetchPortfolio,
}))

mockNuxtImport('useModal', () => () => ({ open: vi.fn() }))

let wrapper: VueWrapper | null = null

describe('investimentos.vue — alocação por classe', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    portfolio.value = null
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('desenha a barra e os percentuais quando a carteira tem base positiva', async () => {
    portfolio.value = {
      total_positions: 3,
      total_cost: 3000,
      by_type: [
        { investment_type: 'stock', count: 2, total_cost: 2000, pct_of_portfolio: 66.7 },
        { investment_type: 'fii', count: 1, total_cost: 1000, pct_of_portfolio: 33.3 },
      ],
    }

    wrapper = await mountSuspended(Investimentos)

    expect(wrapper.find('[data-testid="alloc-sem-base"]').exists()).toBe(false)
    const legenda = wrapper.find('[data-testid="alloc-legenda"]').text()
    expect(legenda).toContain('66.7%')
    expect(legenda).toContain('33.3%')
  })

  it('troca a barra por uma explicação quando o custo líquido da carteira não é positivo', async () => {
    portfolio.value = {
      total_positions: 2,
      total_cost: -500,
      by_type: [
        { investment_type: 'stock', count: 2, total_cost: -500, pct_of_portfolio: null },
      ],
    }

    wrapper = await mountSuspended(Investimentos)

    expect(wrapper.find('[data-testid="alloc-sem-base"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="alloc-sem-base"]').text())
      .toContain('custo líquido da carteira é zero ou negativo')
  })

  // Sem tratamento explícito, o Vue interpola null como string vazia e a legenda
  // fica "Ações %" — um sinal de porcentagem solto, sem número. É menos escandaloso
  // que "null%" e por isso mais fácil de passar batido, então a asserção é sobre a
  // ausência do '%' dentro da legenda, não sobre a ausência da palavra "null".
  it('escreve "—" na legenda, sem sinal de porcentagem solto, quando não há base', async () => {
    portfolio.value = {
      total_positions: 2,
      total_cost: 0,
      by_type: [
        { investment_type: 'stock', count: 2, total_cost: 0, pct_of_portfolio: null },
      ],
    }

    wrapper = await mountSuspended(Investimentos)

    const legenda = wrapper.find('[data-testid="alloc-legenda"]').text()
    expect(legenda).toContain('—')
    expect(legenda).not.toContain('%')
    expect(legenda).not.toContain('null')
  })
})
