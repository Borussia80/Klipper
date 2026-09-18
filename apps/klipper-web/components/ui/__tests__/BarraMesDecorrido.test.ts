/**
 * BarraMesDecorrido tests — régua de ritmo do mês exibido.
 * Mês corrente mostra quanto já passou; mês fechado não tem ritmo a medir
 * e precisa dizer isso, em vez de fingir 100% "decorrido".
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import BarraMesDecorrido from '../BarraMesDecorrido.vue'

describe('BarraMesDecorrido', () => {
  beforeEach(() => {
    // Só Date: fake timers completos travam o flushPromises do Nuxt.
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date(2026, 8, 18)) // 18 de setembro de 2026
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows the elapsed day out of the month length for the current month', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 9 } })
    expect(wrapper.find('[data-testid="ritmo-dia"]').text()).toBe('dia 18 de 30')
  })

  it('shows the elapsed percentage of the current month', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 9 } })
    expect(wrapper.find('[data-testid="ritmo-pct"]').text()).toBe('60% do mês decorrido')
  })

  it('fills the bar with the elapsed percentage', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 9 } })
    expect(wrapper.find('[data-testid="ritmo-fill"]').attributes('style')).toContain('width: 60%')
  })

  it('uses the real length of each month', async () => {
    vi.setSystemTime(new Date(2026, 1, 14)) // 14 de fevereiro de 2026 — 28 dias
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 2 } })
    expect(wrapper.find('[data-testid="ritmo-dia"]').text()).toBe('dia 14 de 28')
    expect(wrapper.find('[data-testid="ritmo-pct"]').text()).toBe('50% do mês decorrido')
  })

  it('announces a closed month instead of a bogus elapsed percentage', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 6 } })
    expect(wrapper.find('[data-testid="ritmo-fechado"]').text()).toContain('mês encerrado')
    expect(wrapper.find('[data-testid="ritmo-dia"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="ritmo-pct"]').exists()).toBe(false)
  })

  it('fills the bar completely and marks it closed for a past month', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 6 } })
    const fill = wrapper.find('[data-testid="ritmo-fill"]')
    expect(fill.attributes('style')).toContain('width: 100%')
    expect(fill.classes()).toContain('fechado')
  })

  it('treats a month of a past year as closed', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2025, month: 9 } })
    expect(wrapper.find('[data-testid="ritmo-fechado"]').exists()).toBe(true)
  })

  it('keeps the values in mono so they line up with the hero', async () => {
    const wrapper = await mountSuspended(BarraMesDecorrido, { props: { year: 2026, month: 9 } })
    expect(wrapper.find('[data-testid="ritmo-pct"]').classes()).toContain('mono')
  })
})
