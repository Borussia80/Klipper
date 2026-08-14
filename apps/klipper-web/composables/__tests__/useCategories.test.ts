import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const mockApiFetch = vi.fn()
const mockAddToast = vi.fn()

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: { value: 'test-token' },
}))

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

function makeCategory(overrides: Partial<{
  id: number
  name: string
  icon: string
  category_type: 'expense' | 'income' | 'transfer'
  natureza: 'fixo' | 'cartao_parcelamento' | 'variavel'
  color: string | null
  active: boolean
  reimbursed_by_category_id: number | null
}> = {}) {
  return {
    id: 1,
    name: 'Terapia Pedro',
    icon: 'health',
    category_type: 'expense' as const,
    natureza: 'fixo' as const,
    color: '#6B93AE',
    active: true,
    reimbursed_by_category_id: null,
    ...overrides,
  }
}

describe('useCategories', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockAddToast.mockReset()
  })

  describe('fetchCategories', () => {
    it('sets isLoading to false and error on a failed fetch', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { isLoading, error, fetchCategories } = useCategories()
      await fetchCategories()
      expect(isLoading.value).toBe(false)
      expect(error.value).toBe('Erro ao carregar categorias.')
    })
  })

  describe('updateCategory', () => {
    it('replaces the matching category in state with the API response', async () => {
      mockApiFetch.mockResolvedValueOnce([makeCategory({ id: 1, reimbursed_by_category_id: null })])
      const updated = makeCategory({ id: 1, reimbursed_by_category_id: 9 })
      mockApiFetch.mockResolvedValueOnce(updated)

      const { categories, fetchCategories, updateCategory } = useCategories()
      await fetchCategories()
      await updateCategory(1, { reimbursed_by_category_id: 9 })

      expect(categories.value[0].reimbursed_by_category_id).toBe(9)
    })

    it('leaves other categories in state untouched', async () => {
      mockApiFetch.mockResolvedValueOnce([
        makeCategory({ id: 1, name: 'Terapia Pedro' }),
        makeCategory({ id: 2, name: 'Mercado' }),
      ])
      mockApiFetch.mockResolvedValueOnce(makeCategory({ id: 1, reimbursed_by_category_id: 9 }))

      const { categories, fetchCategories, updateCategory } = useCategories()
      await fetchCategories()
      await updateCategory(1, { reimbursed_by_category_id: 9 })

      expect(categories.value).toHaveLength(2)
      expect(categories.value.find((c) => c.id === 2)?.name).toBe('Mercado')
    })

    it('calls PATCH on the correct endpoint with the given payload', async () => {
      mockApiFetch.mockResolvedValueOnce(makeCategory({ id: 1, reimbursed_by_category_id: 9 }))

      const { updateCategory } = useCategories()
      await updateCategory(1, { reimbursed_by_category_id: 9 })

      expect(mockApiFetch).toHaveBeenCalledWith('/api/v1/categories/1', {
        method: 'PATCH',
        body: { reimbursed_by_category_id: 9 },
      })
    })

    it('shows a success toast after updating', async () => {
      mockApiFetch.mockResolvedValueOnce(makeCategory({ id: 1, reimbursed_by_category_id: 9 }))

      const { updateCategory } = useCategories()
      await updateCategory(1, { reimbursed_by_category_id: 9 })

      expect(mockAddToast).toHaveBeenCalledWith('Categoria atualizada', 'ok')
    })

    it('propagates API errors without mutating local state', async () => {
      mockApiFetch.mockResolvedValueOnce([makeCategory({ id: 1, name: 'Terapia Pedro' })])
      mockApiFetch.mockRejectedValueOnce(new Error('network error'))

      const { categories, fetchCategories, updateCategory } = useCategories()
      await fetchCategories()

      await expect(updateCategory(1, { reimbursed_by_category_id: 9 })).rejects.toThrow('network error')
      expect(categories.value[0].reimbursed_by_category_id).toBeNull()
    })
  })
})
