/**
 * ModalNovoLancamento tests — verifies the future-date guard actually blocks
 * submission (both via the disabled CTA and via the submit() early-return),
 * and that a valid entry creates the transaction with the expected payload.
 *
 * BaseModal renders through <Teleport to="body">, so we attach to
 * document.body and query through a DOMWrapper, following the pattern in
 * ModalEditarCartao.test.ts.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalNovoLancamento from '../ModalNovoLancamento.vue'

const mockAddToast = vi.fn()
const mockCreateTransaction = vi.fn()
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
  createTransaction: mockCreateTransaction,
}))

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

async function mountModal() {
  wrapper = await mountSuspended(ModalNovoLancamento, { props: { open: true }, attachTo: document.body })
  return wrapper
}

async function fillValidFields() {
  await body.find('input[aria-label="Valor do lançamento em reais"]').setValue('50,00')
  await body.find('input[aria-label="Descrição do lançamento"]').setValue('Supermercado')
}

describe('ModalNovoLancamento', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 7, 15, 12, 0, 0)) // 15/08/2026, meio-dia local
    mockFetchAccounts.mockResolvedValue(undefined)
    mockFetchCategories.mockResolvedValue(undefined)
    mockCreateTransaction.mockResolvedValue({ id: 1 })
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
    vi.useRealTimers()
  })

  it('pré-preenche a data com o dia local de hoje', async () => {
    await mountModal()
    const data = body.find('input[aria-label="Data do lançamento"]').element as HTMLInputElement
    expect(data.value).toBe('2026-08-15')
  })

  it('desabilita o CTA e não envia quando a data é futura', async () => {
    await mountModal()
    await fillValidFields()
    await body.find('input[aria-label="Data do lançamento"]').setValue('2026-08-16')

    const cta = body.find('button.cta').element as HTMLButtonElement
    expect(cta.disabled).toBe(true)

    await body.find('button.cta').trigger('click')
    expect(mockCreateTransaction).not.toHaveBeenCalled()
    expect(mockAddToast).not.toHaveBeenCalled()
  })

  it('habilita o CTA e envia quando todos os campos são válidos, incluindo a data de hoje', async () => {
    const w = await mountModal()
    await fillValidFields()
    await body.find('input[aria-label="Data do lançamento"]').setValue('2026-08-15')

    const cta = body.find('button.cta').element as HTMLButtonElement
    expect(cta.disabled).toBe(false)

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockCreateTransaction).toHaveBeenCalled())

    expect(mockCreateTransaction).toHaveBeenCalledWith(
      expect.objectContaining({ occurred_on: '2026-08-15', transaction_type: 'debit' }),
    )
    expect(w.emitted('close')).toBeTruthy()
  })
})
