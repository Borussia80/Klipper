/**
 * PatrimonioTimeline — React island que renderiza a evolução do patrimônio.
 * UX-5: dados vêm de snapshots mensais reais, sem histórico fabricado; com
 * menos de 2 pontos o gráfico não faz sentido, então mostra um estado vazio.
 */
import { describe, it, expect, afterEach } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import type { VueWrapper } from '@vue/test-utils'
import PatrimonioTimeline from '../PatrimonioTimeline.vue'

describe('PatrimonioTimeline', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
  })

  function styleOf(w: VueWrapper, selector: string) {
    return w.find(selector).attributes('style') ?? ''
  }

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
