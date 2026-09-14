import { describe, it, expect, vi, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import ModalConfirmDelete from '../ModalConfirmDelete.vue'

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

async function mountModal(onConfirm = vi.fn()) {
  wrapper = await mountSuspended(ModalConfirmDelete, {
    props: {
      open: true,
      payload: {
        title: 'Excluir lançamento',
        resourceType: 'lançamento',
        itemName: 'Mercado · R$ 50,00',
        description: 'O lançamento será removido do período atual.',
        onConfirm,
      },
    },
    attachTo: document.body,
  })
  return { wrapper, onConfirm }
}

describe('ModalConfirmDelete', () => {
  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('renderiza uma confirmação destrutiva acessível', async () => {
    await mountModal()

    expect(body.find('[role="dialog"]').exists()).toBe(true)
    expect(body.find('[role="alert"]').exists()).toBe(false)
    expect(body.text()).toContain('Excluir lançamento')
    expect(body.text()).toContain('Mercado · R$ 50,00')
  })

  it('fecha sem confirmar ao cancelar', async () => {
    const { wrapper: w, onConfirm } = await mountModal()

    await body.find('button.btn-g').trigger('click')

    expect(onConfirm).not.toHaveBeenCalled()
    expect(w.emitted('close')).toBeTruthy()
  })

  it('executa a ação confirmada e fecha', async () => {
    const { wrapper: w, onConfirm } = await mountModal(vi.fn().mockResolvedValue(undefined))

    await body.find('button.confirm-danger').trigger('click')

    await vi.waitFor(() => expect(onConfirm).toHaveBeenCalledTimes(1))
    expect(w.emitted('close')).toBeTruthy()
  })

  it('mostra erro quando a exclusão falha', async () => {
    const { wrapper: w } = await mountModal(vi.fn().mockRejectedValue(new Error('fail')))

    await body.find('button.confirm-danger').trigger('click')

    await vi.waitFor(() => expect(body.find('[role="alert"]').text()).toContain('Não foi possível excluir'))
    expect(w.emitted('close')).toBeFalsy()
  })
})
