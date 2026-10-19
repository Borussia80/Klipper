import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import Configuracoes from '../configuracoes.vue'

const mockUser = ref({ id: 1, name: 'Roberto Milet', email: 'roberto@example.com', own_names: ['Roberto'], own_cpf_mask: '123.456' })
const mockUpdateProfile = vi.fn()

mockNuxtImport('useAuth', () => () => ({ user: mockUser, logout: vi.fn(), updateProfile: mockUpdateProfile }))

describe('configuracoes.vue', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('edita perfil e identidade própria, salvando ambos via PATCH', async () => {
    const wrapper = await mountSuspended(Configuracoes)
    await wrapper.get('button.btn-sm').trigger('click')

    expect(wrapper.text()).toContain('Identidade para detectar transferências entre minhas contas')
    expect((wrapper.find('input[aria-label="Nome"]').element as HTMLInputElement).value).toBe('Roberto Milet')
    await wrapper.get('input[aria-label="Nome"]').setValue('Roberto')
    await wrapper.get('form').trigger('submit')

    expect(mockUpdateProfile).toHaveBeenCalledWith(expect.objectContaining({ name: 'Roberto', own_names: ['Roberto'], own_cpf_mask: '123.456' }))
  })
})
