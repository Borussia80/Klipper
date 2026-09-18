/**
 * FluxoMensal — entradas × saídas × resultado, um grupo por mês da janela.
 *
 * O painel respondia só "quanto neste mês". A pergunta que vem depois é de
 * tendência, e ela exige ver os meses lado a lado — inclusive os meses sem
 * nenhum lançamento, que precisam continuar ocupando a sua coluna.
 */
import { describe, it, expect, afterEach } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import type { VueWrapper } from '@vue/test-utils'
import FluxoMensal from '../FluxoMensal.vue'

const JANEIRO_A_JUNHO = [
  { year: 2026, month: 1, total_credits: 4000, total_debits: 3000, net: 1000 },
  { year: 2026, month: 2, total_credits: 0, total_debits: 0, net: 0 },
  { year: 2026, month: 3, total_credits: 4000, total_debits: 5000, net: -1000 },
  { year: 2026, month: 4, total_credits: 4000, total_debits: 2000, net: 2000 },
  { year: 2026, month: 5, total_credits: 0, total_debits: 999, net: -999 },
  { year: 2026, month: 6, total_credits: 5000, total_debits: 2500, net: 2500 },
]

describe('FluxoMensal', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('desenha um grupo por mês, na ordem recebida', async () => {
    wrapper = await mountSuspended(FluxoMensal, { props: { points: JANEIRO_A_JUNHO } })

    const meses = wrapper.findAll('[data-testid="fluxo-mes"]')
    expect(meses).toHaveLength(6)
    expect(meses.map((m) => m.attributes('data-mes'))).toEqual(['1', '2', '3', '4', '5', '6'])
    expect(meses[0]!.text()).toContain('Jan')
    expect(meses[5]!.text()).toContain('Jun')
  })

  it('escala as barras pelo maior valor da janela', async () => {
    wrapper = await mountSuspended(FluxoMensal, { props: { points: JANEIRO_A_JUNHO } })

    const maior = wrapper.findAll('[data-testid="fluxo-mes"]')[5]!
    expect(maior.find('[data-testid="barra-entrada"]').attributes('style')).toContain('height: 100%')

    const marco = wrapper.findAll('[data-testid="fluxo-mes"]')[2]!
    expect(marco.find('[data-testid="barra-saida"]').attributes('style')).toContain('height: 100%')
    expect(marco.find('[data-testid="barra-entrada"]').attributes('style')).toContain('height: 80%')
  })

  // Fevereiro não teve lançamento: a coluna continua lá, vazia. Emendar março em
  // janeiro faria o gráfico contar uma história que não aconteceu.
  it('mantém a coluna do mês sem movimento, sem barra', async () => {
    wrapper = await mountSuspended(FluxoMensal, { props: { points: JANEIRO_A_JUNHO } })

    const fevereiro = wrapper.findAll('[data-testid="fluxo-mes"]')[1]!
    expect(fevereiro.text()).toContain('Fev')
    expect(fevereiro.find('[data-testid="barra-entrada"]').exists()).toBe(false)
    expect(fevereiro.find('[data-testid="barra-saida"]').exists()).toBe(false)
    expect(fevereiro.attributes('class')).toContain('vazio')
  })

  it('marca o mês que fechou no vermelho', async () => {
    wrapper = await mountSuspended(FluxoMensal, { props: { points: JANEIRO_A_JUNHO } })

    const meses = wrapper.findAll('[data-testid="fluxo-mes"]')
    expect(meses[2]!.find('[data-testid="fluxo-net"]').classes()).toContain('neg')
    expect(meses[0]!.find('[data-testid="fluxo-net"]').classes()).not.toContain('neg')
  })

  it('série inteiramente zerada não vira divisão por zero', async () => {
    const zerada = JANEIRO_A_JUNHO.map((p) => ({ ...p, total_credits: 0, total_debits: 0, net: 0 }))

    wrapper = await mountSuspended(FluxoMensal, { props: { points: zerada } })

    expect(wrapper.find('[data-testid="fluxo-vazio"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid="barra-entrada"]')).toHaveLength(0)
  })

  it('descreve a janela para quem lê por leitor de tela', async () => {
    wrapper = await mountSuspended(FluxoMensal, { props: { points: JANEIRO_A_JUNHO } })

    const label = wrapper.find('[role="img"]').attributes('aria-label') ?? ''
    expect(label).toContain('Jan')
    expect(label).toContain('Jun')
  })
})
