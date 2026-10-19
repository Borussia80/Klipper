import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalEditarConta from '../ModalEditarConta.vue'
import type { Account } from '~/composables/useAccounts'

const mockUpdateAccount = vi.fn()

mockNuxtImport('useAccounts', () => () => ({ updateAccount: mockUpdateAccount }))

function account(overrides: Partial<Account> = {}): Account {
  return {
    id: 8,
    name: 'Reserva',
    institution: 'Banco Sintético',
    account_type: 'savings',
    balance: '320.50',
    currency: 'BRL',
    active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    saldo_fatura_atual: null,
    pagamento_minimo: null,
    juros_rotativo_am: null,
    juros_rotativo_aa: null,
    iof_projetado: null,
    saldo_atualizado_em: null,
    ...overrides,
  }
}

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

describe('ModalEditarConta', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUpdateAccount.mockResolvedValue(account())
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('preenche e salva nome, instituição, tipo e saldo da conta', async () => {
    wrapper = await mountSuspended(ModalEditarConta, {
      props: { open: true, account: account() },
      attachTo: document.body,
    })

    await body.find('input[aria-label="Nome da conta"]').setValue('Reserva viagem')
    await body.find('input[aria-label="Instituição financeira"]').setValue('Banco Exemplo')
    await body.find('select[aria-label="Tipo de conta"]').setValue('digital')
    await body.find('input[aria-label="Saldo da conta"]').setValue('850,75')
    await body.find('button.btn-p').trigger('click')

    await vi.waitFor(() => expect(mockUpdateAccount).toHaveBeenCalledWith(8, {
      name: 'Reserva viagem',
      institution: 'Banco Exemplo',
      account_type: 'digital',
      balance: '850.75',
    }))
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
