/**
 * ModalEditarLancamento tests — verifies payload-driven prefill (valor, descrição,
 * categoria, conta, data e tipo) e o submit via updateTransaction, seguindo o
 * mesmo padrão de ModalEditarCartao.test.ts (props-driven) e ModalNovoLancamento.test.ts
 * (mesmos campos de formulário).
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalEditarLancamento from '../ModalEditarLancamento.vue'
import type { Transaction } from '~/composables/useTransactions'

const mockAddToast = vi.fn()
const mockUpdateTransaction = vi.fn()
const mockFetchAccounts = vi.fn()
const mockFetchCategories = vi.fn()

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

mockNuxtImport('useAccounts', () => () => ({
  accounts: { value: [{ id: 1, name: 'Nubank' }] },
  fetchAccounts: mockFetchAccounts,
}))

mockNuxtImport('useCategories', () => () => ({
  categories: { value: [{ id: 1, name: 'Mercado' }] },
  fetchCategories: mockFetchCategories,
}))

mockNuxtImport('useTransactions', () => () => ({
  updateTransaction: mockUpdateTransaction,
}))

function makeTransaction(overrides: Partial<Transaction> = {}): Transaction {
  return {
    id: 42,
    account_id: 1,
    category_id: 1,
    description: 'Mercado',
    amount: '150.00',
    transaction_type: 'debit',
    occurred_on: '2026-08-10',
    notes: null,
    installment_total: null,
    installment_number: null,
    member_id: null,
    ...overrides,
  }
}

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

async function mountModal(props: { open: boolean; transaction: Transaction | null }) {
  wrapper = await mountSuspended(ModalEditarLancamento, { props, attachTo: document.body })
  return wrapper
}

describe('ModalEditarLancamento', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 7, 15, 12, 0, 0)) // 15/08/2026, meio-dia local
    mockFetchAccounts.mockResolvedValue(undefined)
    mockFetchCategories.mockResolvedValue(undefined)
    mockUpdateTransaction.mockResolvedValue(makeTransaction())
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
    vi.useRealTimers()
  })

  it('prefills fields from the transaction payload', async () => {
    await mountModal({ open: true, transaction: makeTransaction() })

    const valor = body.find('input[aria-label="Valor do lançamento em reais"]').element as HTMLInputElement
    const descricao = body.find('input[aria-label="Descrição do lançamento"]').element as HTMLInputElement
    const data = body.find('input[aria-label="Data do lançamento"]').element as HTMLInputElement

    expect(valor.value).toBe('150,00')
    expect(descricao.value).toBe('Mercado')
    expect(data.value).toBe('2026-08-10')
  })

  it('desabilita o CTA e não envia quando a data é futura', async () => {
    await mountModal({ open: true, transaction: makeTransaction() })
    await body.find('input[aria-label="Data do lançamento"]').setValue('2026-08-16')

    const cta = body.find('button.cta').element as HTMLButtonElement
    expect(cta.disabled).toBe(true)

    await body.find('button.cta').trigger('click')
    expect(mockUpdateTransaction).not.toHaveBeenCalled()
  })

  it('submits updateTransaction with the edited fields and closes', async () => {
    const w = await mountModal({ open: true, transaction: makeTransaction() })

    await body.find('input[aria-label="Descrição do lançamento"]').setValue('Mercado (editado)')
    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockUpdateTransaction).toHaveBeenCalled())

    expect(mockUpdateTransaction).toHaveBeenCalledWith(
      42,
      expect.objectContaining({
        description: 'Mercado (editado)',
        amount: '150',
        transaction_type: 'debit',
        occurred_on: '2026-08-10',
      }),
    )
    expect(w.emitted('close')).toBeTruthy()
  })

  it('envia category_id como null (não undefined) ao limpar a categoria', async () => {
    await mountModal({ open: true, transaction: makeTransaction() })

    // A opção "Sem categoria" é a primeira (:value="null") — selecionar por
    // índice evita a ambiguidade de setValue(null) num <select> nativo.
    const select = body.find('select[aria-label="Categoria do lançamento"]').element as HTMLSelectElement
    select.selectedIndex = 0
    await body.find('select[aria-label="Categoria do lançamento"]').trigger('change')

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockUpdateTransaction).toHaveBeenCalled())

    const payload = mockUpdateTransaction.mock.calls[0][1]
    expect(payload.category_id).toBeNull()
  })

  it('shows an error toast when the update fails', async () => {
    mockUpdateTransaction.mockRejectedValue(new Error('network error'))
    const w = await mountModal({ open: true, transaction: makeTransaction() })

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockAddToast).toHaveBeenCalled())

    expect(mockAddToast).toHaveBeenCalledWith('Erro ao salvar. Tente novamente.', 'alert')
    expect(w.emitted('close')).toBeFalsy()
  })
})
