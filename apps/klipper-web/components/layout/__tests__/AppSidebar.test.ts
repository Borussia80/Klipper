/**
 * AppSidebar.vue — UR-5. As ações de criação já existiam na paleta de comandos,
 * atrás de um acionador rotulado "Buscar": ninguém procura cadastrar um cartão
 * numa caixa de busca. A sidebar passou a ter o botão "Criar" com as mesmas
 * ações, e "Novo cartão" abre o modal de conta com o tipo já escolhido.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import AppSidebar from '../AppSidebar.vue'

const mockOpen = vi.fn()

mockNuxtImport('useModal', () => () => ({
  activeModal: ref(null),
  modalPayload: ref(null),
  open: mockOpen,
  close: vi.fn(),
}))

mockNuxtImport('useBudgets', () => () => ({
  summary: ref([]),
  fetchSummary: vi.fn(),
}))

describe('AppSidebar.vue — botão Criar', () => {
  beforeEach(() => vi.clearAllMocks())

  it('só mostra as ações depois de abrir o menu', async () => {
    const wrapper = await mountSuspended(AppSidebar)
    const botao = wrapper.get('button[aria-haspopup="menu"]')

    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
    expect(botao.attributes('aria-expanded')).toBe('false')

    await botao.trigger('click')

    const itens = wrapper.findAll('[role="menuitem"]').map((i) => i.text())
    expect(itens).toEqual(['Novo lançamento', 'Nova conta', 'Novo cartão', 'Novo investimento'])
    expect(botao.attributes('aria-expanded')).toBe('true')
  })

  it('cartão abre o modal de conta já no tipo cartão, e o menu fecha', async () => {
    const wrapper = await mountSuspended(AppSidebar)
    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')

    const cartao = wrapper.findAll('[role="menuitem"]').find((i) => i.text() === 'Novo cartão')
    await cartao!.trigger('click')

    expect(mockOpen).toHaveBeenCalledWith('nova-conta', 'cartao')
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
  })

  it('lançamento e investimento abrem os modais de sempre', async () => {
    const wrapper = await mountSuspended(AppSidebar)

    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')
    await wrapper.findAll('[role="menuitem"]')[0].trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('novo-lancamento', null)

    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')
    const aporte = wrapper.findAll('[role="menuitem"]').find((i) => i.text() === 'Novo investimento')
    await aporte!.trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('novo-aporte', null)
  })
})
