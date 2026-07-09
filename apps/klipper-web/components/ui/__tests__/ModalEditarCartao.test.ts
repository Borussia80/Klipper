/**
 * ModalEditarCartao tests — verifies payload-driven prefill and submit behavior.
 *
 * We mock `useToast` and `useAccounts` via mockNuxtImport so no real HTTP calls
 * happen. `updateAccount` is asserted against the exact 5 debt fields the modal
 * is responsible for editing.
 *
 * BaseModal renders through <Teleport to="body">, so its content lands outside
 * the wrapper's own root element — we attach to document.body and query through
 * a DOMWrapper on document.body instead of `wrapper.find`.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalEditarCartao from '../ModalEditarCartao.vue'

const mockAddToast = vi.fn()
const mockUpdateAccount = vi.fn()

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

mockNuxtImport('useAccounts', () => () => ({
  updateAccount: mockUpdateAccount,
}))

function makeAccount(overrides = {}) {
  return {
    id: 1,
    name: 'Itaú Personnalité',
    institution: 'Itaú',
    account_type: 'credit_card',
    balance: '0.00',
    currency: 'BRL',
    active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    saldo_fatura_atual: '9603.90',
    pagamento_minimo: '960.39',
    juros_rotativo_am: '12.92',
    juros_rotativo_aa: '435.0',
    iof_projetado: '60.12',
    saldo_atualizado_em: '2026-06-01T00:00:00Z',
    ...overrides,
  }
}

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

async function mountModal(props: Record<string, unknown>) {
  wrapper = await mountSuspended(ModalEditarCartao, { props, attachTo: document.body })
  return wrapper
}

describe('ModalEditarCartao', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUpdateAccount.mockResolvedValue(makeAccount())
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('prefills fields from the account payload', async () => {
    await mountModal({ open: true, account: makeAccount() })

    const saldo = body.find('input[aria-label="Saldo da fatura atual"]').element as HTMLInputElement
    const juros = body.find('input[aria-label="Juros do rotativo ao mês, em percentual"]').element as HTMLInputElement

    expect(saldo.value).toBe('9603.9')
    expect(juros.value).toBe('12.92')
  })

  it('leaves fields empty when the account has no debt data yet', async () => {
    await mountModal({
      open: true,
      account: makeAccount({
        saldo_fatura_atual: null,
        pagamento_minimo: null,
        juros_rotativo_am: null,
        juros_rotativo_aa: null,
        iof_projetado: null,
      }),
    })

    const saldo = body.find('input[aria-label="Saldo da fatura atual"]').element as HTMLInputElement
    expect(saldo.value).toBe('')
  })

  it('submits updateAccount with the 5 debt fields as strings', async () => {
    await mountModal({ open: true, account: makeAccount() })

    await body.find('input[aria-label="Saldo da fatura atual"]').setValue('10000')
    await body.find('button.btn-p').trigger('click')
    await vi.waitFor(() => expect(mockUpdateAccount).toHaveBeenCalled())

    expect(mockUpdateAccount).toHaveBeenCalledWith(1, {
      saldo_fatura_atual: '10000',
      pagamento_minimo: '960.39',
      juros_rotativo_am: '12.92',
      juros_rotativo_aa: '435',
      iof_projetado: '60.12',
    })
  })

  it('emits close after a successful submit', async () => {
    const w = await mountModal({ open: true, account: makeAccount() })

    await body.find('button.btn-p').trigger('click')
    await vi.waitFor(() => expect(mockUpdateAccount).toHaveBeenCalled())

    expect(w.emitted('close')).toBeTruthy()
  })

  it('shows an error toast when the update fails', async () => {
    mockUpdateAccount.mockRejectedValue(new Error('network error'))
    const w = await mountModal({ open: true, account: makeAccount() })

    await body.find('button.btn-p').trigger('click')
    await vi.waitFor(() => expect(mockAddToast).toHaveBeenCalled())

    expect(mockAddToast).toHaveBeenCalledWith('Erro ao salvar. Tente novamente.', 'alert')
    expect(w.emitted('close')).toBeFalsy()
  })
})
