/**
 * Onboarding tests — UX-1: só oferece como "conectável" banco com adapter de
 * import real (app/services/pdf_adapters/registry.rb), e os badges usam o
 * componente UiBankIcon (ícone real do banco) em vez de letra hardcoded.
 */
import { describe, it, expect, vi } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import Onboarding from '../onboarding.vue'
import BankIcon from '../../components/ui/BankIcon.vue'

mockNuxtImport('useOnboarding', () => () => ({
  completeOnboarding: vi.fn(),
}))

mockNuxtImport('useToast', () => () => ({
  addToast: vi.fn(),
}))

describe('onboarding.vue — step 1 (conectar banco)', () => {
  it('lists only banks with a real import adapter', async () => {
    const wrapper = await mountSuspended(Onboarding)

    const cards = wrapper.findAll('.bank-card')
    const names = cards.map((c) => c.text())

    expect(names).toHaveLength(3)
    expect(names.some((n) => n.includes('Nubank'))).toBe(true)
    expect(names.some((n) => n.includes('Itaú'))).toBe(true)
    expect(names.some((n) => n.includes('BTG'))).toBe(true)

    // Bancos sem adapter (registry.rb só tem Itau/Nubank/BTG) não aparecem mais.
    expect(names.some((n) => n.includes('Bradesco'))).toBe(false)
    expect(names.some((n) => n.includes('Santander'))).toBe(false)
    expect(names.some((n) => n.includes('C6'))).toBe(false)
  })

  it('renders bank badges via UiBankIcon instead of a hardcoded letter', async () => {
    const wrapper = await mountSuspended(Onboarding)

    const cards = wrapper.findAll('.bank-card')
    expect(cards).toHaveLength(3)
    cards.forEach((card) => {
      expect(card.findComponent(BankIcon).exists()).toBe(true)
    })
  })
})
