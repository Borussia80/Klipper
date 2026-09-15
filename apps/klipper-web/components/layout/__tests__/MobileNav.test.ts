import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import MobileNav from '../MobileNav.vue'

describe('MobileNav.vue', () => {
  it('disponibiliza os destinos principais na barra', async () => {
    const wrapper = await mountSuspended(MobileNav)

    expect(wrapper.get('a[aria-label="Painel"]').attributes('href')).toBe('/dashboard')
    expect(wrapper.get('a[aria-label="Movimento"]').attributes('href')).toBe('/transacoes')
    expect(wrapper.get('a[aria-label="Orçamento"]').attributes('href')).toBe('/orcamento')
    expect(wrapper.get('a[aria-label="Investimentos"]').attributes('href')).toBe('/investimentos')
  })

  it('só mostra os destinos secundários depois de abrir Mais', async () => {
    const wrapper = await mountSuspended(MobileNav)

    expect(wrapper.find('a[href="/relatorios"]').exists()).toBe(false)

    await wrapper.get('button[aria-label="Mais páginas"]').trigger('click')

    expect(wrapper.get('a[href="/relatorios"]')).toBeTruthy()
    expect(wrapper.get('a[href="/importar"]')).toBeTruthy()
    expect(wrapper.get('a[href="/portadores"]')).toBeTruthy()
    expect(wrapper.get('a[href="/configuracoes"]')).toBeTruthy()
    expect(wrapper.get('a[href="/contas"]')).toBeTruthy()
  })

  it('fecha a folha ao escolher um destino secundário', async () => {
    const wrapper = await mountSuspended(MobileNav)
    await wrapper.get('button[aria-label="Mais páginas"]').trigger('click')

    await wrapper.get('a[href="/relatorios"]').trigger('click')

    expect(wrapper.find('section[aria-label="Mais páginas"]').exists()).toBe(false)
  })
})
