import { describe, it, expect, vi } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import AppTopbar from '../AppTopbar.vue'

const mockNavigateTo = vi.fn()
mockNuxtImport('useConnectionStatus', () => () => ({ isOffline: ref(false) }))
mockNuxtImport('useAuth', () => () => ({ user: ref({ name: 'Ana Beatriz', email: 'ana@example.com' }) }))
mockNuxtImport('navigateTo', () => (...args: unknown[]) => mockNavigateTo(...args))

describe('AppTopbar', () => {
  it('mostra as iniciais do usuário e abre configurações ao clicar no avatar', async () => {
    const wrapper = await mountSuspended(AppTopbar)
    const avatar = wrapper.get('button.btn-avatar')
    expect(avatar.text()).toContain('AB')
    expect(avatar.attributes('aria-label')).toContain('Ana Beatriz')
    await avatar.trigger('click')
    expect(mockNavigateTo).toHaveBeenCalledWith('/configuracoes')
  })
})
