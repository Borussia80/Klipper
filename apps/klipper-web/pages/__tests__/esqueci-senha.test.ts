import { describe, it, expect, vi } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import EsqueciSenha from '../esqueci-senha.vue'

const requestPasswordReset = vi.fn()

mockNuxtImport('useAuth', () => () => ({
  requestPasswordReset,
}))

describe('esqueci-senha.vue', () => {
  it('shows the generic success message after submitting an e-mail', async () => {
    requestPasswordReset.mockResolvedValueOnce(undefined)
    const wrapper = await mountSuspended(EsqueciSenha)

    await wrapper.find('input[type="email"]').setValue('roberto@example.com')
    await wrapper.find('button.btn-p').trigger('click')
    await vi.waitFor(() => expect(requestPasswordReset).toHaveBeenCalledWith('roberto@example.com'))
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Se o e-mail existir, enviaremos um link de redefinição.')
  })

  it('shows an error message when the request fails', async () => {
    requestPasswordReset.mockRejectedValueOnce(new Error('network error'))
    const wrapper = await mountSuspended(EsqueciSenha)

    await wrapper.find('input[type="email"]').setValue('roberto@example.com')
    await wrapper.find('button.btn-p').trigger('click')
    await vi.waitFor(() => expect(requestPasswordReset).toHaveBeenCalled())
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Não foi possível processar o pedido.')
  })
})
