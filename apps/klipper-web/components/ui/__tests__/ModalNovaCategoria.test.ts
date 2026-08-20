/**
 * ModalNovaCategoria tests — trava a regressão P0.3 (limite mensal descartado
 * ao criar categoria): submit() deve chamar createCategory e, em seguida,
 * createBudget com o category_id retornado e o mês/ano corrente. Quando o
 * createBudget falha, a categoria já persistida não é revertida — o modal
 * fecha normalmente, mas com um toast explícito de que o limite NÃO foi
 * salvo (sem sucesso falso).
 *
 * BaseModal renders through <Teleport to="body">, attach document.body query
 * through DOMWrapper, pattern in ModalNovoLancamento.test.ts.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalNovaCategoria from '../ModalNovaCategoria.vue'

const mockAddToast = vi.fn()
const mockCreateCategory = vi.fn()
const mockCreateBudget = vi.fn()
const mockFetchCategories = vi.fn()

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

mockNuxtImport('useCategories', () => () => ({
  incomes: { value: [] },
  fetchCategories: mockFetchCategories,
  createCategory: mockCreateCategory,
}))

mockNuxtImport('useBudgets', () => () => ({
  createBudget: mockCreateBudget,
}))

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

async function mountModal() {
  wrapper = await mountSuspended(ModalNovaCategoria, { props: { open: true }, attachTo: document.body })
  return wrapper
}

async function fillValidFields() {
  await body.find('input[aria-label="Nome da categoria"]').setValue('Restaurantes')
  await body.find('input[aria-label="Limite mensal em reais"]').setValue('500,00')
}

describe('ModalNovaCategoria', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 7, 15, 12, 0, 0)) // 15/08/2026, meio-dia local
    mockFetchCategories.mockResolvedValue(undefined)
    mockCreateCategory.mockResolvedValue({ id: 42, name: 'Restaurantes' })
    mockCreateBudget.mockResolvedValue({ id: 1 })
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
    vi.useRealTimers()
  })

  it('cria a categoria e em seguida o orçamento do mês corrente com o category_id retornado', async () => {
    const w = await mountModal()
    await fillValidFields()

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockCreateBudget).toHaveBeenCalled())

    expect(mockCreateCategory).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'Restaurantes' }),
    )
    expect(mockCreateBudget).toHaveBeenCalledWith({
      category_id: 42,
      amount_limit: '500.00',
      period_month: 8,
      period_year: 2026,
    })
    expect(w.emitted('close')).toBeTruthy()
  })

  it('mantém a categoria criada e mostra falha parcial quando o orçamento não pode ser salvo', async () => {
    mockCreateBudget.mockRejectedValue(new Error('unprocessable'))
    const w = await mountModal()
    await fillValidFields()

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockCreateBudget).toHaveBeenCalled())

    expect(mockCreateCategory).toHaveBeenCalled()
    expect(mockAddToast).toHaveBeenCalledWith(
      'Categoria criada, mas não foi possível definir o limite mensal. Ajuste em Orçamento.',
      'alert',
    )
    // categoria já foi persistida com sucesso — não há motivo para travar o usuário no modal
    expect(w.emitted('close')).toBeTruthy()
  })

  it('não chama createBudget quando a criação da categoria falha', async () => {
    mockCreateCategory.mockRejectedValue(new Error('unprocessable'))
    const w = await mountModal()
    await fillValidFields()

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockAddToast).toHaveBeenCalled())

    expect(mockCreateBudget).not.toHaveBeenCalled()
    expect(mockAddToast).toHaveBeenCalledWith('Erro ao salvar. Tente novamente.', 'alert')
    expect(w.emitted('close')).toBeFalsy()
  })
})
