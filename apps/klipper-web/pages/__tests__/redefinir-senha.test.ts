import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import RedefinirSenha from '../redefinir-senha.vue'

const confirmPasswordReset = vi.fn()
const mockNavigateTo = vi.fn()
const routeQuery = { token: 'valid-token' as string | undefined }

mockNuxtImport('useAuth', () => () => ({
  confirmPasswordReset,
}))

mockNuxtImport('useRoute', () => () => ({
  query: routeQuery,
}))

mockNuxtImport('navigateTo', () => (...args: unknown[]) => mockNavigateTo(...args))

describe('redefinir-senha.vue', () => {
  beforeEach(() => {
    confirmPasswordReset.mockReset()
    mockNavigateTo.mockReset()
    routeQuery.token = 'valid-token'
  })

  it('shows an invalid-link message when there is no token in the URL', async () => {
    routeQuery.token = undefined
    const wrapper = await mountSuspended(RedefinirSenha)

    expect(wrapper.text()).toContain('Link inválido.')
    expect(wrapper.find('input[type="password"]').exists()).toBe(false)
  })

  it('shows an error when the passwords do not match', async () => {
    const wrapper = await mountSuspended(RedefinirSenha)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('newpass456')
    await passwordInputs[1].setValue('somethingelse')
    await wrapper.find('button.btn-p').trigger('click')

    expect(wrapper.text()).toContain('As senhas não conferem.')
    expect(confirmPasswordReset).not.toHaveBeenCalled()
  })

  it('confirms the reset and redirects to /login on success', async () => {
    confirmPasswordReset.mockResolvedValueOnce(undefined)
    const wrapper = await mountSuspended(RedefinirSenha)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('newpass456')
    await passwordInputs[1].setValue('newpass456')
    await wrapper.find('button.btn-p').trigger('click')

    await vi.waitFor(() =>
      expect(confirmPasswordReset).toHaveBeenCalledWith('valid-token', 'newpass456', 'newpass456'),
    )
    expect(mockNavigateTo).toHaveBeenCalledWith('/login')
  })

  it('shows a backend error message when the token is invalid or expired', async () => {
    confirmPasswordReset.mockRejectedValueOnce({ data: { error: 'Link inválido ou expirado' } })
    const wrapper = await mountSuspended(RedefinirSenha)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('newpass456')
    await passwordInputs[1].setValue('newpass456')
    await wrapper.find('button.btn-p').trigger('click')

    await vi.waitFor(() => expect(confirmPasswordReset).toHaveBeenCalled())
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Link inválido ou expirado')
  })
})
