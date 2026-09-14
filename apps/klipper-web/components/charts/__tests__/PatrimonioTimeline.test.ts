/**
 * PatrimonioTimeline — gráfico de evolução do patrimônio em SVG nativo.
 * UX-5: dados vêm de snapshots mensais reais, sem histórico fabricado; com
 * menos de 2 pontos o gráfico não faz sentido, então mostra um estado vazio.
 *
 * Os testes de desenho só são possíveis porque o gráfico é SVG no template.
 * Na versão anterior (island React montado via createRoot) nada disso era
 * visível ao wrapper — a suíte passava mesmo se o gráfico não desenhasse nada.
 */
import { describe, it, expect, afterEach } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import type { VueWrapper } from '@vue/test-utils'
import PatrimonioTimeline from '../PatrimonioTimeline.vue'

const TRES_PONTOS = [
  { date: 'Jun/26', value: 1000 },
  { date: 'Jul/26', value: 1200 },
  { date: 'Ago/26', value: 900 },
]

describe('PatrimonioTimeline', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
  })

  function styleOf(w: VueWrapper, selector: string) {
    return w.find(selector).attributes('style') ?? ''
  }

  describe('estado vazio', () => {
    it('shows the empty state when there are no data points', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: [] } })
      expect(styleOf(wrapper, '[data-testid="timeline-empty"]')).not.toContain('display: none')
      expect(styleOf(wrapper, '.timeline-host')).toContain('display: none')
    })

    it('shows the empty state when there is only one data point', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, {
        props: { data: [ { date: 'Jul/26', value: 1000 } ] },
      })
      expect(styleOf(wrapper, '[data-testid="timeline-empty"]')).not.toContain('display: none')
      expect(styleOf(wrapper, '.timeline-host')).toContain('display: none')
    })

    it('hides the empty state once there are 2 or more data points', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, {
        props: {
          data: [
            { date: 'Jun/26', value: 1000 },
            { date: 'Jul/26', value: 1200 },
          ],
        },
      })
      expect(styleOf(wrapper, '[data-testid="timeline-empty"]')).toContain('display: none')
      expect(styleOf(wrapper, '.timeline-host')).not.toContain('display: none')
    })
  })

  describe('desenho', () => {
    it('traça a linha com um vértice por ponto de dado', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: TRES_PONTOS } })

      const d = wrapper.find('[data-testid="timeline-line"]').attributes('d') ?? ''
      // um "M" inicial + um "L" por ponto seguinte
      expect(d).toMatch(/^M/)
      expect(d.match(/L/g)?.length).toBe(TRES_PONTOS.length - 1)
    })

    it('fecha a área sob a linha para receber o gradiente', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: TRES_PONTOS } })

      const d = wrapper.find('[data-testid="timeline-area"]').attributes('d') ?? ''
      expect(d).toMatch(/Z$/)
    })

    it('rotula o eixo X com as datas recebidas', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: TRES_PONTOS } })

      const labels = wrapper.findAll('[data-testid="x-tick"]').map(n => n.text())
      expect(labels).toContain('Jun/26')
      expect(labels).toContain('Ago/26')
    })

    it('rotula o eixo Y em BRL compacto, cobrindo a faixa dos dados', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: TRES_PONTOS } })

      const ticks = wrapper.findAll('[data-testid="y-tick"]')
      expect(ticks.length).toBeGreaterThanOrEqual(2)
      expect(ticks.every(t => t.text().includes('R$'))).toBe(true)

      // toda marca nomeia um valor que o gráfico alcança: o domínio precisa
      // conter o mínimo (900) e o máximo (1200) da série
      const valores = ticks.map(t => Number(t.attributes('data-value')))
      expect(Math.min(...valores)).toBeLessThanOrEqual(900)
      expect(Math.max(...valores)).toBeGreaterThanOrEqual(1200)
    })

    it('descreve o gráfico para leitor de tela', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: TRES_PONTOS } })

      const svg = wrapper.find('[data-testid="timeline-svg"]')
      expect(svg.attributes('role')).toBe('img')
      expect(svg.attributes('aria-label')).toBeTruthy()
    })
  })

  describe('reatividade', () => {
    it('redesenha quando os dados mudam', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, {
        props: { data: TRES_PONTOS.slice(0, 2) },
      })
      const antes = wrapper.find('[data-testid="timeline-line"]').attributes('d')

      await wrapper.setProps({ data: TRES_PONTOS })
      const depois = wrapper.find('[data-testid="timeline-line"]').attributes('d')

      expect(depois).not.toBe(antes)
      expect(wrapper.findAll('[data-testid="x-tick"]').length).toBe(TRES_PONTOS.length)
    })

    it('volta ao estado vazio se a série encolher para menos de 2 pontos', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, { props: { data: TRES_PONTOS } })
      expect(styleOf(wrapper, '.timeline-host')).not.toContain('display: none')

      await wrapper.setProps({ data: [] })
      expect(styleOf(wrapper, '.timeline-host')).toContain('display: none')
      expect(styleOf(wrapper, '[data-testid="timeline-empty"]')).not.toContain('display: none')
    })
  })

  describe('série degenerada', () => {
    it('não quebra quando todos os valores são iguais', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, {
        props: {
          data: [
            { date: 'Jun/26', value: 500 },
            { date: 'Jul/26', value: 500 },
          ],
        },
      })

      const d = wrapper.find('[data-testid="timeline-line"]').attributes('d') ?? ''
      expect(d).not.toContain('NaN')
      expect(d).not.toContain('Infinity')
    })

    it('não quebra quando os valores são zero', async () => {
      wrapper = await mountSuspended(PatrimonioTimeline, {
        props: {
          data: [
            { date: 'Jun/26', value: 0 },
            { date: 'Jul/26', value: 0 },
          ],
        },
      })

      const d = wrapper.find('[data-testid="timeline-line"]').attributes('d') ?? ''
      expect(d).not.toContain('NaN')
    })
  })
})
