/**
 * useAccounts tests — verifies state management and API integration.
 *
 * We mock `useApi` and `useToast` via mockNuxtImport so that the composable
 * never makes real HTTP calls. Each test gets a fresh mock via beforeEach.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

// ── mock setup ──────────────────────────────────────────────────────────────

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

// ── helpers ─────────────────────────────────────────────────────────────────

function makeAccount(overrides: Partial<{
  id: number
  name: string
  institution: string
  account_type: string
  balance: string
  currency: string
  active: boolean
  created_at: string
  updated_at: string
}> = {}) {
  return {
    id: 1,
    name: 'Nubank',
    institution: 'nubank',
    account_type: 'digital',
    balance: '1000.00',
    currency: 'BRL',
    active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

// ── tests ────────────────────────────────────────────────────────────────────

describe('useAccounts', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockAddToast.mockReset()
  })

  // ── fetchAccounts ──────────────────────────────────────────────────────────

  describe('fetchAccounts', () => {
    it('populates accounts state with API response', async () => {
      mockApiFetch.mockResolvedValue([makeAccount()])
      const { accounts, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(accounts.value).toHaveLength(1)
      expect(accounts.value[0].name).toBe('Nubank')
    })

    it('replaces accounts on subsequent fetch', async () => {
      mockApiFetch.mockResolvedValueOnce([makeAccount({ id: 1, name: 'A' })])
      const { accounts, fetchAccounts } = useAccounts()
      await fetchAccounts()

      mockApiFetch.mockResolvedValueOnce([makeAccount({ id: 2, name: 'B' }), makeAccount({ id: 3, name: 'C' })])
      await fetchAccounts()
      expect(accounts.value).toHaveLength(2)
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue([])
      const { isLoading, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(isLoading.value).toBe(false)
    })

    it('sets isLoading to false after a failed fetch', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { isLoading, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(isLoading.value).toBe(false)
    })

    it('sets error state on API failure', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { error, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(error.value).toBeTruthy()
    })

    it('clears error state before a new fetch', async () => {
      mockApiFetch.mockRejectedValueOnce(new Error('fail'))
      const { error, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(error.value).toBeTruthy()

      mockApiFetch.mockResolvedValueOnce([])
      await fetchAccounts()
      expect(error.value).toBeNull()
    })
  })

  // ── totalBalance ───────────────────────────────────────────────────────────

  describe('totalBalance', () => {
    it('sums all account balances as a number', async () => {
      mockApiFetch.mockResolvedValue([
        makeAccount({ id: 1, balance: '1000.00' }),
        makeAccount({ id: 2, balance: '500.50' }),
      ])
      const { totalBalance, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(totalBalance.value).toBeCloseTo(1500.5)
    })

    it('returns 0 when accounts list is empty', async () => {
      mockApiFetch.mockResolvedValue([])
      const { totalBalance, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(totalBalance.value).toBe(0)
    })

    it('handles a single account correctly', async () => {
      mockApiFetch.mockResolvedValue([makeAccount({ balance: '250.75' })])
      const { totalBalance, fetchAccounts } = useAccounts()
      await fetchAccounts()
      expect(totalBalance.value).toBeCloseTo(250.75)
    })
  })

  // ── createAccount ──────────────────────────────────────────────────────────

  describe('createAccount', () => {
    it('appends the new account to accounts state', async () => {
      mockApiFetch.mockResolvedValueOnce([]) // fetchAccounts
      const newAccount = makeAccount({ id: 99, name: 'Itaú' })
      mockApiFetch.mockResolvedValueOnce(newAccount)

      const { accounts, fetchAccounts, createAccount } = useAccounts()
      await fetchAccounts()
      await createAccount({ name: 'Itaú', institution: 'itau', account_type: 'checking', currency: 'BRL' })

      expect(accounts.value.find((a) => a.id === 99)).toBeDefined()
      expect(accounts.value.find((a) => a.name === 'Itaú')).toBeDefined()
    })

    it('shows a success toast after creating an account', async () => {
      const newAccount = makeAccount({ id: 10, name: 'XP' })
      mockApiFetch.mockResolvedValue(newAccount)

      const { createAccount } = useAccounts()
      await createAccount({ name: 'XP', account_type: 'investment', currency: 'BRL' })

      expect(mockAddToast).toHaveBeenCalledWith('Conta adicionada', 'ok')
    })

    it('returns the created account', async () => {
      const newAccount = makeAccount({ id: 55, name: 'Inter' })
      mockApiFetch.mockResolvedValue(newAccount)

      const { createAccount } = useAccounts()
      const result = await createAccount({ name: 'Inter' })
      expect(result.id).toBe(55)
    })
  })

  // ── updateAccount ──────────────────────────────────────────────────────────

  describe('updateAccount', () => {
    it('replaces the matching account in state', async () => {
      mockApiFetch.mockResolvedValueOnce([makeAccount({ id: 1, name: 'Old Name' })])
      const updated = makeAccount({ id: 1, name: 'New Name' })
      mockApiFetch.mockResolvedValueOnce(updated)

      const { accounts, fetchAccounts, updateAccount } = useAccounts()
      await fetchAccounts()
      await updateAccount(1, { name: 'New Name' })

      expect(accounts.value[0].name).toBe('New Name')
    })

    it('shows success toast after update', async () => {
      mockApiFetch.mockResolvedValueOnce([makeAccount({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(makeAccount({ id: 1, name: 'Updated' }))

      const { fetchAccounts, updateAccount } = useAccounts()
      await fetchAccounts()
      await updateAccount(1, { name: 'Updated' })

      expect(mockAddToast).toHaveBeenCalledWith('Conta atualizada', 'ok')
    })
  })

  // ── deleteAccount ──────────────────────────────────────────────────────────

  describe('deleteAccount', () => {
    it('removes the account from state', async () => {
      mockApiFetch.mockResolvedValueOnce([
        makeAccount({ id: 1, name: 'Keep' }),
        makeAccount({ id: 2, name: 'Delete Me' }),
      ])
      mockApiFetch.mockResolvedValueOnce(undefined) // DELETE response

      const { accounts, fetchAccounts, deleteAccount } = useAccounts()
      await fetchAccounts()
      await deleteAccount(2)

      expect(accounts.value).toHaveLength(1)
      expect(accounts.value[0].id).toBe(1)
    })

    it('shows success toast after deletion', async () => {
      mockApiFetch.mockResolvedValueOnce([makeAccount({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { fetchAccounts, deleteAccount } = useAccounts()
      await fetchAccounts()
      await deleteAccount(1)

      expect(mockAddToast).toHaveBeenCalledWith('Conta removida', 'ok')
    })
  })
})
