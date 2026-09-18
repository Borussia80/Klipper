/**
 * InstrumentReadout tests — hero faceplate do dashboard (direção náutica premium):
 * label, valor com sinal, barra de faixa clampada em [0,1] (over acima de 100%)
 * e pernas (entradas/saídas) opcionais em mono.
 */
import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import InstrumentReadout from '../InstrumentReadout.vue'

const baseProps = {
  label: 'Resultado do mês · operacional',
  netValue: -1711,
  formattedValue: '−R$ 1.711,00',
  spentRatio: 1.12,
}

describe('InstrumentReadout', () => {
  it('renders label and formatted value', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.text()).toContain('Resultado do mês · operacional')
    expect(wrapper.text()).toContain('−R$ 1.711,00')
  })

  it('applies the neg class when netValue is negative', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.find('.hero-num').classes()).toContain('neg')
  })

  it('applies the pos class when netValue is positive', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: { ...baseProps, netValue: 4500, formattedValue: 'R$ 4.500,00', spentRatio: 0.4 },
    })
    expect(wrapper.find('.hero-num').classes()).toContain('pos')
  })

  it('sets the bar width from spentRatio', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: { ...baseProps, spentRatio: 0.65 },
    })
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.attributes('style')).toContain('width: 65%')
  })

  it('clamps spentRatio above 1 to 100% and adds the over class', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.attributes('style')).toContain('width: 100%')
    expect(bar.classes()).toContain('over')
  })

  it('clamps negative spentRatio to 0% and omits the over class', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: { ...baseProps, spentRatio: -0.4 },
    })
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.attributes('style')).toContain('width: 0%')
    expect(bar.classes()).not.toContain('over')
  })

  it('renders each leg with its label and value in mono', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: {
        ...baseProps,
        legs: [
          { label: 'Entradas', value: 'R$ 13.804,00', tone: 'ok' as const },
          { label: 'Saídas', value: 'R$ 15.515,00', tone: 'sea' as const },
        ],
      },
    })
    const legs = wrapper.findAll('[data-testid="readout-leg"]')
    expect(legs).toHaveLength(2)
    expect(legs[0]!.text()).toContain('Entradas')
    expect(legs[0]!.text()).toContain('R$ 13.804,00')
    expect(legs[0]!.find('.leg-val').classes()).toContain('mono')
    expect(legs[1]!.text()).toContain('Saídas')
    expect(legs[1]!.text()).toContain('R$ 15.515,00')
  })

  it('paints each leg with its own tone', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: {
        ...baseProps,
        legs: [
          { label: 'Entradas', value: 'R$ 13.804,00', tone: 'ok' as const },
          { label: 'Saídas', value: 'R$ 15.515,00', tone: 'sea' as const },
        ],
      },
    })
    const legs = wrapper.findAll('[data-testid="readout-leg"]')
    expect(legs[0]!.find('.leg-val').classes()).toContain('ok')
    expect(legs[1]!.find('.leg-val').classes()).toContain('sea')
  })

  it('omits the legs row when no legs are given', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.find('[data-testid="readout-leg"]').exists()).toBe(false)
  })

  it('applies the compact class when compact is true', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: { ...baseProps, compact: true } })
    expect(wrapper.find('.hero').classes()).toContain('compact')
  })

  it('omits the compact class by default', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.find('.hero').classes()).not.toContain('compact')
  })

  it('omits the bar and scale when showBar is false', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: { ...baseProps, showBar: false } })
    expect(wrapper.find('[data-testid="readout-bar"]').exists()).toBe(false)
    expect(wrapper.find('.hero-scale').exists()).toBe(false)
  })

  it('renders the bar and scale by default', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.find('[data-testid="readout-bar"]').exists()).toBe(true)
    expect(wrapper.find('.hero-scale').exists()).toBe(true)
  })

  it('FIN-3: shows a distinct "sem orçamento definido" state when spentRatio is null, instead of an empty bar', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: { ...baseProps, spentRatio: null } })
    expect(wrapper.find('[data-testid="readout-no-budget"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Sem orçamento definido')
    expect(wrapper.find('[data-testid="readout-bar"]').exists()).toBe(false)
    expect(wrapper.find('.hero-scale').exists()).toBe(false)
  })

  it('FIN-3: renders the bar normally when spentRatio is 0 (real zero spend, distinct from null)', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: { ...baseProps, spentRatio: 0 } })
    expect(wrapper.find('[data-testid="readout-bar"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="readout-no-budget"]').exists()).toBe(false)
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.attributes('style')).toContain('width: 0%')
  })
})
