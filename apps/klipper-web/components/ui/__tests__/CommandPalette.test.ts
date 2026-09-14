import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import CommandPalette from '../CommandPalette.vue'

const mockOpen = vi.fn()

mockNuxtImport('useModal', () => () => ({
  open: mockOpen,
  close: vi.fn(),
  activeModal: { value: null },
}))

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

describe('CommandPalette.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  async function mountPalette(open = true) {
    wrapper = await mountSuspended(CommandPalette, {
      props: { open },
      attachTo: document.body,
    })
    return wrapper
  }

  it('renderiza os comandos e atalhos disponíveis ao abrir', async () => {
    await mountPalette(true)
    const items = body.findAll('.cp-item')
    expect(items.length).toBeGreaterThan(5)
    expect(body.text()).toContain('Novo Lançamento')
    expect(body.text()).toContain('Ir para o Painel')
  })

  it('possui atributos de acessibilidade combobox/listbox com aria-activedescendant', async () => {
    await mountPalette(true)
    const input = body.find('.cp-input')
    expect(input.attributes('role')).toBe('combobox')
    expect(input.attributes('aria-expanded')).toBe('true')
    expect(input.attributes('aria-controls')).toBe('cp-results-list')
    expect(input.attributes('aria-activedescendant')).toBe('cp-item-act-novo-lancamento')

    const firstItem = body.find('#cp-item-act-novo-lancamento')
    expect(firstItem.exists()).toBe(true)
    expect(firstItem.attributes('role')).toBe('option')
  })

  it('filtra comandos dinamicamente de acordo com o texto digitado', async () => {
    await mountPalette(true)
    const input = body.find('.cp-input')
    await input.setValue('invest')

    const items = body.findAll('.cp-item')
    expect(items.length).toBeGreaterThanOrEqual(1)
    expect(body.text()).toContain('Investimentos')
    expect(body.text()).not.toContain('Novo Lançamento')
    expect(input.attributes('aria-activedescendant')).toBe('cp-item-act-novo-aporte')
  })

  it('executa a ação ao clicar no item e emite evento de fechar', async () => {
    const w = await mountPalette(true)
    const itemNovoLancamento = body.findAll('.cp-item')[0]
    await itemNovoLancamento.trigger('click')

    expect(mockOpen).toHaveBeenCalledWith('novo-lancamento')
    expect(w.emitted('close')).toBeTruthy()
  })

  it('executa comando de navegação chamando router.push e fecha', async () => {
    const w = await mountPalette(true)
    const router = w.vm.$router
    const pushSpy = vi.spyOn(router, 'push').mockResolvedValue(undefined)

    const input = body.find('.cp-input')
    await input.setValue('Painel')

    const itemDashboard = body.findAll('.cp-item')[0]
    await itemDashboard.trigger('click')

    expect(pushSpy).toHaveBeenCalledWith('/dashboard')
    expect(w.emitted('close')).toBeTruthy()
  })

  it('prende o foco de Tab dentro do palette (não escapa pro conteúdo atrás)', async () => {
    wrapper = await mountSuspended(CommandPalette, { props: { open: false }, attachTo: document.body })
    await wrapper.setProps({ open: true })
    await nextTick()
    await nextTick()

    const items = body.findAll('.cp-item')
    const lastItem = items[items.length - 1].element as HTMLElement
    lastItem.focus()
    expect(document.activeElement).toBe(lastItem)

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true }))

    const input = body.find('.cp-input').element
    expect(document.activeElement).toBe(input)
  })

  it('devolve o foco pro elemento que abriu o palette, ao fechar', async () => {
    const trigger = document.createElement('button')
    document.body.appendChild(trigger)
    trigger.focus()

    wrapper = await mountSuspended(CommandPalette, { props: { open: false }, attachTo: document.body })
    await wrapper.setProps({ open: true })
    await nextTick()
    await nextTick()

    await wrapper.setProps({ open: false })

    expect(document.activeElement).toBe(trigger)
    trigger.remove()
  })

  it('navega pelas setas de teclado e seleciona com Enter', async () => {
    const w = await mountPalette(true)
    const dialog = body.find('.cp-dialog')

    // Pressiona seta para baixo duas vezes
    await dialog.trigger('keydown', { key: 'ArrowDown' })
    await dialog.trigger('keydown', { key: 'ArrowDown' })

    // Pressiona Enter
    await dialog.trigger('keydown', { key: 'Enter' })

    expect(mockOpen).toHaveBeenCalled()
    expect(w.emitted('close')).toBeTruthy()
  })
})
