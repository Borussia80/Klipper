/**
 * useOnboarding tests — verifica que o finish() do onboarding de fato persiste
 * dados (conta por banco selecionado, categoria + orçamento a partir da meta).
 *
 * Mocka useApi/useToast (via mockNuxtImport) para nunca fazer chamada real.
 */
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

describe('useOnboarding', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockAddToast.mockReset()
  })

  it('creates one account per selected bank', async () => {
    mockApiFetch.mockResolvedValue({ id: 1 })
    const { completeOnboarding } = useOnboarding()

    await completeOnboarding({ bankNames: ['Nubank', 'Itaú'], goal: null, savingsGoal: '' })

    const accountCalls = mockApiFetch.mock.calls.filter(([url]) => url === '/api/v1/accounts')
    expect(accountCalls).toHaveLength(2)
    expect(accountCalls[0][1].body).toMatchObject({ name: 'Nubank', institution: 'Nubank', account_type: 'checking' })
  })

  it('creates no account when no bank is selected', async () => {
    const { completeOnboarding } = useOnboarding()
    await completeOnboarding({ bankNames: [], goal: null, savingsGoal: '' })
    expect(mockApiFetch).not.toHaveBeenCalled()
  })

  it('creates a category from the selected goal', async () => {
    mockApiFetch.mockResolvedValue({ id: 42 })
    const { completeOnboarding } = useOnboarding()

    await completeOnboarding({
      bankNames: [],
      goal: { id: 'reserva', icon: 'target', label: 'Reserva de emergência' },
      savingsGoal: '',
    })

    const categoryCalls = mockApiFetch.mock.calls.filter(([url]) => url === '/api/v1/categories')
    expect(categoryCalls).toHaveLength(1)
    expect(categoryCalls[0][1].body).toMatchObject({
      name: 'Reserva de emergência',
      icon: 'target',
      category_type: 'expense',
      natureza: 'fixo',
    })
  })

  it('creates a budget for the goal category when savingsGoal is a valid amount', async () => {
    mockApiFetch.mockResolvedValueOnce({ id: 42 }) // createCategory
    mockApiFetch.mockResolvedValueOnce({ id: 7 }) // createBudget
    const { completeOnboarding } = useOnboarding()

    await completeOnboarding({
      bankNames: [],
      goal: { id: 'reserva', icon: 'target', label: 'Reserva de emergência' },
      savingsGoal: '500,50',
    })

    const budgetCalls = mockApiFetch.mock.calls.filter(([url]) => url === '/api/v1/budgets')
    expect(budgetCalls).toHaveLength(1)
    expect(budgetCalls[0][1].body).toMatchObject({ category_id: 42, amount_limit: '500.50' })
  })

  it('does not create a budget when savingsGoal is empty or zero', async () => {
    mockApiFetch.mockResolvedValueOnce({ id: 42 }) // createCategory
    const { completeOnboarding } = useOnboarding()

    await completeOnboarding({
      bankNames: [],
      goal: { id: 'reserva', icon: 'target', label: 'Reserva de emergência' },
      savingsGoal: '0',
    })

    const budgetCalls = mockApiFetch.mock.calls.filter(([url]) => url === '/api/v1/budgets')
    expect(budgetCalls).toHaveLength(0)
  })

  it('does nothing when no goal and no banks are selected', async () => {
    const { completeOnboarding } = useOnboarding()
    await completeOnboarding({ bankNames: [], goal: null, savingsGoal: '' })
    expect(mockApiFetch).not.toHaveBeenCalled()
  })
})
