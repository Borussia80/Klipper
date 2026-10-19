import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import Orcamento from '../orcamento.vue'

const mockFetchSummary = vi.fn()
const mockFetchCategories = vi.fn()
const mockFetchReimbursementCoverage = vi.fn()

mockNuxtImport('useBudgets', () => () => ({
  summary: ref([]), isLoading: ref(false), error: ref(null), fetchSummary: mockFetchSummary,
}))
mockNuxtImport('useCategories', () => () => ({ fetchCategories: mockFetchCategories }))
mockNuxtImport('useReports', () => () => ({
  reimbursementCoverage: ref(null), fetchReimbursementCoverage: mockFetchReimbursementCoverage,
}))

describe('orcamento.vue — seletor de período', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 9, 15, 12, 0, 0))
  })

  afterEach(() => vi.useRealTimers())

  it('recarrega resumo e reembolsos ao navegar para o mês anterior e voltar ao atual', async () => {
    const wrapper = await mountSuspended(Orcamento)
    expect(mockFetchSummary).toHaveBeenCalledWith(2026, 10)
    expect(mockFetchReimbursementCoverage).toHaveBeenCalledWith(2026, 10)

    await wrapper.find('button[aria-label="Mês anterior"]').trigger('click')
    expect(mockFetchSummary).toHaveBeenLastCalledWith(2026, 9)
    expect(mockFetchReimbursementCoverage).toHaveBeenLastCalledWith(2026, 9)

    await wrapper.find('button[aria-label="Mês atual"]').trigger('click')
    expect(mockFetchSummary).toHaveBeenLastCalledWith(2026, 10)
  })
})
