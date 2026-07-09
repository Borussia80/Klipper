/**
 * DebtRankingCard tests — BRL/percent formatting, rank styling, estimate-label
 * variations and stale-data highlighting.
 */
import { describe, it, expect, vi, afterEach } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import DebtRankingCard from '../DebtRankingCard.vue'

function makeRow(overrides = {}) {
  return {
    account_id: 1,
    name: 'Itaú Personnalité',
    institution: 'Itaú',
    saldo_fatura_atual: 9603.90,
    pagamento_minimo: 960.39,
    juros_rotativo_am: 12.92,
    juros_rotativo_aa: 435.0,
    iof_projetado: 60.12,
    encargos: 1116.98,
    saldo_projetado_proximo_mes: 10781.00,
    saldo_atualizado_em: '2026-07-01T00:00:00Z',
    ...overrides,
  }
}

describe('DebtRankingCard', () => {
  afterEach(() => vi.useRealTimers())

  it('formats saldo_fatura_atual and encargos in BRL', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow() },
    })
    expect(wrapper.text()).toMatch(/9\.603,90/)
    expect(wrapper.text()).toMatch(/1\.116,98/)
  })

  it('formats saldo_projetado_proximo_mes in BRL', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow() },
    })
    expect(wrapper.text()).toMatch(/10\.781,00/)
  })

  it('shows the rank badge as 1-indexed', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 2, row: makeRow() },
    })
    expect(wrapper.text()).toContain('#3')
  })

  it('applies the alert border class only to rank 0', async () => {
    const first = await mountSuspended(DebtRankingCard, { props: { rank: 0, row: makeRow() } })
    const second = await mountSuspended(DebtRankingCard, { props: { rank: 1, row: makeRow() } })
    expect(first.find('.bc').classes()).toContain('bc-a')
    expect(second.find('.bc').classes()).not.toContain('bc-a')
  })

  it('labels as plain estimate when iof and minimo are both present', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, { props: { rank: 0, row: makeRow() } })
    expect(wrapper.text()).toContain('(estimativa)')
  })

  it('labels missing IOF when iof_projetado is null', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ iof_projetado: null }) },
    })
    expect(wrapper.text()).toContain('(estimativa sem IOF)')
  })

  it('labels missing minimo when pagamento_minimo is null', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ pagamento_minimo: null }) },
    })
    expect(wrapper.text()).toContain('(estimativa sem pagamento mínimo capturado)')
  })

  it('labels both missing when iof and minimo are both null', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ iof_projetado: null, pagamento_minimo: null }) },
    })
    expect(wrapper.text()).toContain('(estimativa sem IOF nem pagamento mínimo capturados)')
  })

  it('highlights stale data older than 30 days', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 6, 8))
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ saldo_atualizado_em: new Date(2026, 4, 1).toISOString() }) },
    })
    expect(wrapper.text()).toMatch(/atualizado há \d+ meses/)
  })

  it('does not render a freshness indicator when saldo_atualizado_em is null', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ saldo_atualizado_em: null }) },
    })
    expect(wrapper.text()).not.toMatch(/atualizado/)
  })

  it('does not mark exactly 30 days old as stale', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 6, 8))
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ saldo_atualizado_em: new Date(2026, 5, 8).toISOString() }) },
    })
    expect(wrapper.html()).not.toContain('var(--warn)')
  })

  it('marks 31 days old as stale', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 6, 8))
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ saldo_atualizado_em: new Date(2026, 5, 7).toISOString() }) },
    })
    expect(wrapper.html()).toContain('var(--warn)')
  })

  it('hides the a.a. suffix when juros_rotativo_aa is null', async () => {
    const wrapper = await mountSuspended(DebtRankingCard, {
      props: { rank: 0, row: makeRow({ juros_rotativo_aa: null }) },
    })
    expect(wrapper.text()).not.toContain('a.a.')
  })
})
