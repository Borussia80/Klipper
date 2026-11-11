import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import { flushPromises } from '@vue/test-utils'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import MobileNav from '../MobileNav.vue'
import { useModal } from '~/composables/useModal'

describe('MobileNav.vue', () => {
  it('disponibiliza os destinos principais na barra', async () => {
    const wrapper = await mountSuspended(MobileNav)

    expect(wrapper.get('a[aria-label="Painel"]').attributes('href')).toBe('/dashboard')
    expect(wrapper.get('a[aria-label="Movimento"]').attributes('href')).toBe('/transacoes')
    expect(wrapper.get('a[aria-label="Orçamento"]').attributes('href')).toBe('/orcamento')
    expect(wrapper.find('a[aria-label="Investimentos"]').exists()).toBe(false)
    const items = wrapper.get('nav').findAll('a, button')
    expect(items.map(item => item.attributes('aria-label'))).toEqual([
      'Painel', 'Movimento', 'Novo lançamento', 'Orçamento', 'Mais páginas',
    ])
    await wrapper.get('button[aria-label="Novo lançamento"]').trigger('click')
    expect(useModal().activeModal.value).toBe('novo-lancamento')
    useModal().close()
  })

  it('só mostra os destinos secundários depois de abrir Mais', async () => {
    const wrapper = await mountSuspended(MobileNav)

    expect(wrapper.find('a[href="/relatorios"]').exists()).toBe(false)

    await wrapper.get('button[aria-label="Mais páginas"]').trigger('click')

    expect(wrapper.get('a[href="/relatorios"]')).toBeTruthy()
    expect(wrapper.get('a[href="/importar"]')).toBeTruthy()
    expect(wrapper.get('a[href="/portadores"]')).toBeTruthy()
    expect(wrapper.get('a[href="/configuracoes"]')).toBeTruthy()
    expect(wrapper.get('a[href="/contas"]').text()).toBe('Contas')
    expect(wrapper.get('a[href="/investimentos"]')).toBeTruthy()
  })

  // UXR-12: a folha "Mais" é um diálogo navegável por teclado.
  it('abre "Mais" como diálogo, com o foco dentro e retorno ao gatilho ao fechar com Esc', async () => {
    const wrapper = await mountSuspended(MobileNav, { attachTo: document.body })
    const trigger = wrapper.get('button[aria-label="Mais páginas"]')
    ;(trigger.element as HTMLElement).focus()

    await trigger.trigger('click')
    await nextTick()

    const sheet = wrapper.get('section[aria-label="Mais páginas"]')
    expect(sheet.attributes('role')).toBe('dialog')
    expect(sheet.attributes('aria-modal')).toBe('true')
    expect(sheet.element.contains(document.activeElement)).toBe(true)

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await nextTick()

    expect(wrapper.find('section[aria-label="Mais páginas"]').exists()).toBe(false)
    expect(document.activeElement).toBe(trigger.element)
    wrapper.unmount()
  })

  it('fecha "Mais" quando a página muda por outro caminho', async () => {
    const wrapper = await mountSuspended(MobileNav)
    await wrapper.get('button[aria-label="Mais páginas"]').trigger('click')
    expect(wrapper.find('section[aria-label="Mais páginas"]').exists()).toBe(true)

    // Rota pública: no teste não há sessão, e o middleware desviaria uma rota protegida para /login.
    await useRouter().push('/esqueci-senha')
    await flushPromises()

    expect(wrapper.find('section[aria-label="Mais páginas"]').exists()).toBe(false)
  })

  it('fecha a folha ao escolher um destino secundário', async () => {
    const wrapper = await mountSuspended(MobileNav)
    await wrapper.get('button[aria-label="Mais páginas"]').trigger('click')

    await wrapper.get('a[href="/relatorios"]').trigger('click')

    expect(wrapper.find('section[aria-label="Mais páginas"]').exists()).toBe(false)
  })
})
