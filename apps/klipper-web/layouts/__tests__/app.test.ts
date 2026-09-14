/**
 * layouts/app.vue — atalhos de teclado globais.
 *
 * Regressão 1: os branches de navegação por letra única (t/d/o/i) não checavam
 * modificadores, então Alt+D (foca a barra de endereço no Firefox/Chrome em
 * Windows/Linux) era sequestrado e navegava para /dashboard em vez de deixar
 * o navegador tratar o atalho. O guard agora é único, antes do switch.
 *
 * Regressão 2: Cmd+K rodava antes da checagem de `activeModal`, então com um
 * modal já aberto (ex: "Novo Lançamento" em preenchimento) ele era trocado
 * silenciosamente pela command palette, descartando o que a pessoa digitou.
 * Agora o guard de `activeModal` vem primeiro — Cmd+K continua funcionando
 * com um input comum focado (busca global), só não troca um modal aberto.
 *
 * Os componentes filhos pesados (Topbar, Sidebar, MobileNav, ModalMount,
 * ToastStack) são stubados — o que se testa aqui é só o handler de teclado
 * do próprio layout, não a árvore inteira de composables que eles usam.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import type { VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import AppLayout from '../app.vue'

const mockOpen = vi.fn()
const mockActiveModal = ref<string | null>(null)

mockNuxtImport('useModal', () => () => ({
  open: mockOpen,
  close: vi.fn(),
  activeModal: mockActiveModal,
  modalPayload: ref(null),
}))

let wrapper: VueWrapper | null = null

// useRouter fica real (o mock global quebra plugins internos do Nuxt que também
// chamam useRouter().afterEach/beforeResolve durante o bootstrap do app). Em vez
// disso, espiona-se o router real que o próprio componente resolve.
async function mountLayout() {
  wrapper = await mountSuspended(AppLayout, {
    slots: { default: () => 'conteúdo' },
    global: {
      stubs: {
        LayoutAppTopbar: true,
        LayoutAppSidebar: true,
        LayoutMobileNav: true,
        UiModalMount: true,
        UiToastStack: true,
      },
    },
  })
  const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockResolvedValue(undefined)
  return { wrapper, pushSpy }
}

function pressKey(key: string, modifiers: Partial<KeyboardEventInit> = {}) {
  const event = new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true, ...modifiers })
  document.dispatchEvent(event)
  return event
}

describe('layouts/app.vue — atalhos de teclado globais', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockActiveModal.value = null
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('navega para /dashboard ao pressionar "d" sem modificador', async () => {
    const { pushSpy } = await mountLayout()
    const event = pressKey('d')

    expect(pushSpy).toHaveBeenCalledWith('/dashboard')
    expect(event.defaultPrevented).toBe(true)
  })

  it('não sequestra Alt+D (atalho nativo de foco na barra de endereço)', async () => {
    const { pushSpy } = await mountLayout()
    const event = pressKey('d', { altKey: true })

    expect(pushSpy).not.toHaveBeenCalled()
    expect(event.defaultPrevented).toBe(false)
  })

  it('não sequestra Ctrl+T nem Cmd+O', async () => {
    const { pushSpy } = await mountLayout()
    pressKey('t', { ctrlKey: true })
    pressKey('o', { metaKey: true })

    expect(pushSpy).not.toHaveBeenCalled()
  })

  it('não troca um modal já aberto pela command palette ao pressionar Cmd+K', async () => {
    mockActiveModal.value = 'novo-lancamento'
    await mountLayout()
    pressKey('k', { metaKey: true })

    expect(mockOpen).not.toHaveBeenCalledWith('command-palette')
  })

  it('abre a command palette com Cmd+K mesmo com um input comum focado (sem modal aberto)', async () => {
    await mountLayout()
    const input = document.createElement('input')
    document.body.appendChild(input)
    input.focus()

    pressKey('k', { metaKey: true })

    expect(mockOpen).toHaveBeenCalledWith('command-palette')
    input.remove()
  })

  it('ignora atalhos de letra única quando já há um modal aberto', async () => {
    mockActiveModal.value = 'novo-lancamento'
    const { pushSpy } = await mountLayout()
    pressKey('d')

    expect(pushSpy).not.toHaveBeenCalled()
  })
})
