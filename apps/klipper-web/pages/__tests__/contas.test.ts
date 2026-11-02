import { describe, it, expect, vi, afterEach } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import type { VueWrapper } from '@vue/test-utils'
import Contas from '../contas/index.vue'

mockNuxtImport('useAccounts', () => () => ({
  accounts: ref([
    { id: 1, name: 'Conta futura', account_type: 'checking', balance: null },
    { id: 2, name: 'Cartão futuro', account_type: 'credit_card', balance: null },
    { id: 3, name: 'Conta atual', account_type: 'checking', balance: '125.50' },
  ]),
  isLoading: ref(false), error: ref(null), fetchAccounts: vi.fn(), deleteAccount: vi.fn(),
}))
mockNuxtImport('useReports', () => () => ({ debtRanking: ref(null), fetchDebtRanking: vi.fn() }))
mockNuxtImport('useModal', () => () => ({ open: vi.fn() }))

let wrapper: VueWrapper | null = null
afterEach(() => { wrapper?.unmount(); wrapper = null })

describe('contas — saldo antes da abertura', () => {
  it('distingue ausência de saldo de um valor existente em contas e cartões', async () => {
    wrapper = await mountSuspended(Contas)
    const rows = wrapper.findAll('.ac')
    expect(rows[0].text()).toContain('Sem saldo nesta data')
    expect(rows[1].text()).toContain('125,50')
    expect(rows[2].text()).toContain('Sem saldo nesta data')
    expect(wrapper.text()).not.toContain('NaN')
  })
})
