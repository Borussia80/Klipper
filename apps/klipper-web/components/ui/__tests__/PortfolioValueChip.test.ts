/**
 * PortfolioValueChip tests — header de investimentos.vue.
 * Corrige o bug do roadmap: total real formatado + chip neutro de variação
 * (não há current_price/histórico no backend, então nunca se inventa um percentual).
 */
import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import PortfolioValueChip from '../PortfolioValueChip.vue'

describe('PortfolioValueChip', () => {
  it('renders the formatted total cost', async () => {
    const wrapper = await mountSuspended(PortfolioValueChip, { props: { totalCost: 187654.32 } })
    expect(wrapper.text()).toMatch(/R\$/)
    expect(wrapper.text()).toMatch(/187\.654,32/)
  })

  it('renders 0,00 when totalCost is 0', async () => {
    const wrapper = await mountSuspended(PortfolioValueChip, { props: { totalCost: 0 } })
    expect(wrapper.text()).toMatch(/0,00/)
  })

  it('renders the neutral variation chip instead of a percentage', async () => {
    const wrapper = await mountSuspended(PortfolioValueChip, { props: { totalCost: 128050 } })
    expect(wrapper.text()).toContain('Variação indisponível — histórico insuficiente')
  })

  it('never renders the old hardcoded placeholder values', async () => {
    const wrapper = await mountSuspended(PortfolioValueChip, { props: { totalCost: 128050 } })
    expect(wrapper.text()).not.toContain('187.400')
    expect(wrapper.text()).not.toContain('14,2%')
  })
})
