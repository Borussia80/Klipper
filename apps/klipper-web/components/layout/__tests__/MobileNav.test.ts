import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import MobileNav from '../MobileNav.vue'

describe('MobileNav.vue', () => {
  it('mantém quatro entradas fixas e reúne as páginas secundárias em Mais', async () => {
    const wrapper = await mountSuspended(MobileNav)

    expect(wrapper.findAll('.mobile-nav-item')).toHaveLength(5)
    expect(wrapper.findAll('.mobile-nav-item:not(.more-trigger)').map((item) => item.attributes('href')))
      .toEqual(['/dashboard', '/transacoes', '/orcamento', '/investimentos'])

    await wrapper.find('.more-trigger').trigger('click')

    expect(wrapper.find('.more-sheet').exists()).toBe(true)
    expect(wrapper.findAll('.more-item').map((item) => item.attributes('href')))
      .toEqual(['/relatorios', '/importar', '/portadores', '/configuracoes', '/contas'])
  })
})
