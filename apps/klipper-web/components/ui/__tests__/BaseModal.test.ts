// Spec 02 (aceite 4) e UXR-07: no celular, a ação principal de um formulário
// fica num rodapé fixo, fora da área que rola, para continuar ao alcance do
// polegar mesmo com o teclado aberto.
import { afterEach, describe, expect, it } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { h } from 'vue'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import BaseModal from '../BaseModal.vue'

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

afterEach(() => {
  wrapper?.unmount()
  wrapper = null
})

describe('BaseModal', () => {
  it('mostra a ação do rodapé fora da área rolável', async () => {
    wrapper = await mountSuspended(BaseModal, {
      props: { title: 'Teste', open: true },
      slots: {
        default: () => h('p', { class: 'conteudo' }, 'Campos'),
        footer: () => h('button', { class: 'acao' }, 'Salvar'),
      },
      attachTo: document.body,
    })

    const footer = body.get('[role="dialog"] .drawer-footer')
    expect(footer.find('button.acao').exists()).toBe(true)
    expect(body.get('.drawer-body').find('button.acao').exists()).toBe(false)
    expect(body.get('.drawer-body').find('.conteudo').exists()).toBe(true)
  })

  it('não cria rodapé quando o formulário não tem ação fixa', async () => {
    wrapper = await mountSuspended(BaseModal, {
      props: { title: 'Teste', open: true },
      slots: { default: () => h('p', 'Campos') },
      attachTo: document.body,
    })

    expect(body.find('[role="dialog"]').exists()).toBe(true)
    expect(body.find('.drawer-footer').exists()).toBe(false)
  })
})
