import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalEditarMembro from '../ModalEditarMembro.vue'
import type { Member } from '~/composables/useMembers'

const mockUpdateMember = vi.fn()

mockNuxtImport('useMembers', () => () => ({ updateMember: mockUpdateMember }))

const member: Member = {
  id: 4,
  name: 'Pessoa Sintética',
  relationship: 'dependente',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

describe('ModalEditarMembro', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUpdateMember.mockResolvedValue(member)
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('salva o nome editado do portador', async () => {
    wrapper = await mountSuspended(ModalEditarMembro, {
      props: { open: true, member },
      attachTo: document.body,
    })

    await body.find('input[aria-label="Nome do portador"]').setValue('Pessoa Atualizada')
    await body.find('button.btn-p').trigger('click')

    await vi.waitFor(() => expect(mockUpdateMember).toHaveBeenCalledWith(4, { name: 'Pessoa Atualizada' }))
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
