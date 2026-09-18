/**
 * DataHealthBanner — a faixa que explica por que as telas estão vazias.
 *
 * 338 de 345 transações importadas entraram sem categoria. Orçamento e
 * relatórios ficam vazios por consequência disso, mas o painel não dizia nada,
 * e o usuário conclui que o app não funciona. O número vai para a tela.
 */
import { describe, it, expect, afterEach } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import type { VueWrapper } from '@vue/test-utils'
import DataHealthBanner from '../DataHealthBanner.vue'

describe('DataHealthBanner', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('diz quantas transações estão sem categoria e o que isso custa', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 345, uncategorized: 338, without_account: 345 } },
    })

    expect(wrapper.text()).toContain('338 de 345')
    expect(wrapper.text()).toContain('orçamento')
    expect(wrapper.find('a[href="/transacoes"]').exists()).toBe(true)
  })

  it('some quando está tudo categorizado', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 345, uncategorized: 0, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  // Base vazia é o estado do usuário novo: a faixa falaria de um problema que
  // ele ainda não tem.
  it('some quando não há transação nenhuma', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 0, uncategorized: 0, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  it('não desenha nada enquanto a contagem não chegou', async () => {
    wrapper = await mountSuspended(DataHealthBanner, { props: { health: null } })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  // Uma minoria sem categoria não justifica uma faixa de alerta no painel: o
  // aviso é para o caso em que a categorização é o que está travando as telas.
  it('não alarma quando a maior parte já está categorizada', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 345, uncategorized: 12, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  it('mostra a proporção como barra', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 100, uncategorized: 75, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health-bar"]').attributes('style')).toContain('width: 75%')
  })
})
