/**
 * InstrumentReadout tests — o instrumento primário de cada tela (padrão HMI):
 * label, valor, barra de faixa com ratio clampado em [0,1] e detalhe opcional.
 */
import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import InstrumentReadout from '../InstrumentReadout.vue'

const baseProps = {
  label: 'Livre para gastar',
  value: 'R$ 4.820,00',
  ratio: 0.59,
}

describe('InstrumentReadout', () => {
  it('renders label and value', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.text()).toContain('Livre para gastar')
    expect(wrapper.text()).toContain('R$ 4.820,00')
  })

  it('sets the range bar width from ratio', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.exists()).toBe(true)
    expect(bar.attributes('style')).toContain('width: 59%')
  })

  it('clamps ratio above 1 to 100%', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: { ...baseProps, ratio: 1.8 },
    })
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.attributes('style')).toContain('width: 100%')
  })

  it('clamps negative ratio to 0%', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: { ...baseProps, ratio: -0.4 },
    })
    const bar = wrapper.find('[data-testid="readout-bar"]')
    expect(bar.attributes('style')).toContain('width: 0%')
  })

  it('renders detail text when provided', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, {
      props: { ...baseProps, detail: 'R$ 8.740 gastos · R$ 12.300 recebidos' },
    })
    expect(wrapper.text()).toContain('R$ 8.740 gastos · R$ 12.300 recebidos')
  })

  it('omits detail element when not provided', async () => {
    const wrapper = await mountSuspended(InstrumentReadout, { props: baseProps })
    expect(wrapper.find('[data-testid="readout-detail"]').exists()).toBe(false)
  })
})
