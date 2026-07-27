/**
 * KpiCard tests — card presentational da grid de 3 KPIs do dashboard.
 * chipTone 'neutral' (ou ausente) renderiza texto simples; ok/warn/alert
 * renderizam um chip colorido.
 */
import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import KpiCard from '../KpiCard.vue'

describe('KpiCard', () => {
  it('renders label and value', async () => {
    const wrapper = await mountSuspended(KpiCard, {
      props: { label: 'Salário (OTAMERICA)', icon: 'income', value: 'R$ 12.604' },
    })
    expect(wrapper.text()).toContain('Salário (OTAMERICA)')
    expect(wrapper.text()).toContain('R$ 12.604')
  })

  it('renders a colored chip when chipTone is ok/warn/alert', async () => {
    const wrapper = await mountSuspended(KpiCard, {
      props: { label: 'Compromissos fixos', icon: 'home', value: 'R$ 8.132', chipText: '65% da renda', chipTone: 'warn' },
    })
    const chip = wrapper.find('.chip')
    expect(chip.exists()).toBe(true)
    expect(chip.classes()).toContain('warn')
    expect(chip.text()).toBe('65% da renda')
  })

  it('renders plain footer text without a chip when chipTone is neutral', async () => {
    const wrapper = await mountSuspended(KpiCard, {
      props: { label: 'Salário', icon: 'income', value: 'R$ 12.604', chipText: 'recebido dia 29', chipTone: 'neutral' },
    })
    expect(wrapper.find('.chip').exists()).toBe(false)
    expect(wrapper.text()).toContain('recebido dia 29')
  })

  it('renders plain footer text when chipTone is omitted', async () => {
    const wrapper = await mountSuspended(KpiCard, {
      props: { label: 'Salário', icon: 'income', value: 'R$ 12.604', chipText: 'recebido dia 29' },
    })
    expect(wrapper.find('.chip').exists()).toBe(false)
    expect(wrapper.text()).toContain('recebido dia 29')
  })

  it('omits the footer entirely when chipText is not provided', async () => {
    const wrapper = await mountSuspended(KpiCard, {
      props: { label: 'Salário', icon: 'income', value: 'R$ 12.604' },
    })
    expect(wrapper.find('.kpi-foot').exists()).toBe(false)
  })
})
