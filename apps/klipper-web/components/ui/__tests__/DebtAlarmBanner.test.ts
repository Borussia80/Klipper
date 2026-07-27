/**
 * DebtAlarmBanner tests — alarme acionável do dashboard.
 * Não existe campo de vencimento de fatura no sistema: a copy nunca pode
 * dizer "vence em", só encargos/saldo/juros do rotativo (dados reais).
 */
import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import DebtAlarmBanner from '../DebtAlarmBanner.vue'
import type { DebtRankingRow } from '../../../composables/useReports'

function makeRow(overrides: Partial<DebtRankingRow> = {}): DebtRankingRow {
  return {
    account_id: 1,
    name: 'Itaú Personnalité',
    institution: 'Itaú',
    saldo_fatura_atual: 9603.90,
    pagamento_minimo: 960.39,
    juros_rotativo_am: 12.92,
    juros_rotativo_aa: 338.0,
    iof_projetado: 60.12,
    encargos: 1116.98,
    saldo_projetado_proximo_mes: 10781.00,
    saldo_atualizado_em: '2026-07-01T12:00:00Z',
    ...overrides,
  }
}

describe('DebtAlarmBanner', () => {
  it('renders the card name', async () => {
    const wrapper = await mountSuspended(DebtAlarmBanner, { props: { row: makeRow() } })
    expect(wrapper.text()).toContain('Itaú Personnalité')
  })

  it('never mentions a due date, since the field does not exist in the system', async () => {
    const wrapper = await mountSuspended(DebtAlarmBanner, { props: { row: makeRow() } })
    expect(wrapper.text().toLowerCase()).not.toContain('vence')
  })

  it('formats encargos as BRL', async () => {
    const wrapper = await mountSuspended(DebtAlarmBanner, { props: { row: makeRow() } })
    expect(wrapper.text()).toContain('1.116,98')
  })

  it('renders juros_rotativo_aa when present', async () => {
    const wrapper = await mountSuspended(DebtAlarmBanner, { props: { row: makeRow() } })
    expect(wrapper.text()).toContain('a.a.')
  })

  it('omits the a.a. suffix cleanly when juros_rotativo_aa is null', async () => {
    const wrapper = await mountSuspended(DebtAlarmBanner, {
      props: { row: makeRow({ juros_rotativo_aa: null }) },
    })
    expect(wrapper.text()).not.toContain('a.a.')
    expect(wrapper.text()).not.toContain('null')
    expect(wrapper.text()).not.toContain('NaN')
  })

  it('links to /contas', async () => {
    const wrapper = await mountSuspended(DebtAlarmBanner, { props: { row: makeRow() } })
    const link = wrapper.find('a.alarm-cta')
    expect(link.exists()).toBe(true)
    expect(link.attributes('href')).toBe('/contas')
  })
})
