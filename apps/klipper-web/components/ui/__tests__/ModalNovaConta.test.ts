/**
 * ModalNovaConta.vue — UR-5. O item "Novo cartão" da sidebar abre este mesmo
 * modal (cartão mora em accounts), então o tipo precisa chegar escolhido; sem
 * isso o usuário pede cartão e recebe um formulário de conta corrente.
 */
import { describe, it, expect, vi, afterEach } from 'vitest'
import { ref } from 'vue'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalNovaConta from '../ModalNovaConta.vue'

// BaseModal renderiza através de <Teleport to="body">: a consulta vai no body,
// mesmo padrão de ModalNovaCategoria.test.ts.
const body = new DOMWrapper(document.body)
let wrapper: VueWrapper | null = null

mockNuxtImport('useAccounts', () => () => ({
  accounts: ref([]),
  createAccount: vi.fn(),
}))

mockNuxtImport('useToast', () => () => ({
  addToast: vi.fn(),
}))

describe('ModalNovaConta.vue — tipo pré-escolhido', () => {
  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('abre em cartão de crédito quando veio do item Novo cartão', async () => {
    wrapper = await mountSuspended(ModalNovaConta, {
      props: { open: false, presetTipo: 'cartao' },
      attachTo: document.body,
    })

    await wrapper.setProps({ open: true })

    expect((body.get('select[aria-label="Tipo de conta"]').element as HTMLSelectElement).value).toBe('cartao')
  })

  it('abre em conta corrente quando veio de Nova conta', async () => {
    wrapper = await mountSuspended(ModalNovaConta, {
      props: { open: false, presetTipo: null },
      attachTo: document.body,
    })

    await wrapper.setProps({ open: true })

    expect((body.get('select[aria-label="Tipo de conta"]').element as HTMLSelectElement).value).toBe('corrente')
  })
})
