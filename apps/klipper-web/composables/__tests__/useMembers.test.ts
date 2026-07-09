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

function makeMember(overrides: Partial<{
  id: number
  name: string
  relationship: 'titular' | 'dependente'
  active: boolean
  created_at: string
  updated_at: string
}> = {}) {
  return {
    id: 1,
    name: 'Roberto Milet',
    relationship: 'titular' as const,
    active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

describe('useMembers', () => {
  beforeEach(() => {
    mockApiFetch.mockReset()
    mockAddToast.mockReset()
  })

  describe('fetchMembers', () => {
    it('populates members state with API response', async () => {
      mockApiFetch.mockResolvedValue([makeMember()])
      const { members, fetchMembers } = useMembers()
      await fetchMembers()
      expect(members.value).toHaveLength(1)
      expect(members.value[0].name).toBe('Roberto Milet')
    })

    it('replaces members on subsequent fetch', async () => {
      mockApiFetch.mockResolvedValueOnce([makeMember({ id: 1, name: 'A' })])
      const { members, fetchMembers } = useMembers()
      await fetchMembers()

      mockApiFetch.mockResolvedValueOnce([makeMember({ id: 2, name: 'B' }), makeMember({ id: 3, name: 'C' })])
      await fetchMembers()
      expect(members.value).toHaveLength(2)
    })

    it('sets isLoading to false after successful fetch', async () => {
      mockApiFetch.mockResolvedValue([])
      const { isLoading, fetchMembers } = useMembers()
      await fetchMembers()
      expect(isLoading.value).toBe(false)
    })

    it('sets error state on API failure', async () => {
      mockApiFetch.mockRejectedValue(new Error('network error'))
      const { error, fetchMembers } = useMembers()
      await fetchMembers()
      expect(error.value).toBeTruthy()
    })

    it('clears error state before a new fetch', async () => {
      mockApiFetch.mockRejectedValueOnce(new Error('fail'))
      const { error, fetchMembers } = useMembers()
      await fetchMembers()
      expect(error.value).toBeTruthy()

      mockApiFetch.mockResolvedValueOnce([])
      await fetchMembers()
      expect(error.value).toBeNull()
    })
  })

  describe('createMember', () => {
    it('appends the new member to members state', async () => {
      mockApiFetch.mockResolvedValueOnce([])
      const newMember = makeMember({ id: 99, name: 'Clarea Ana Almeida' })
      mockApiFetch.mockResolvedValueOnce(newMember)

      const { members, fetchMembers, createMember } = useMembers()
      await fetchMembers()
      await createMember({ name: 'Clarea Ana Almeida', relationship: 'dependente' })

      expect(members.value.find((m) => m.id === 99)).toBeDefined()
    })

    it('shows a success toast after creating a member', async () => {
      const newMember = makeMember({ id: 10, name: 'Lara' })
      mockApiFetch.mockResolvedValue(newMember)

      const { createMember } = useMembers()
      await createMember({ name: 'Lara', relationship: 'dependente' })

      expect(mockAddToast).toHaveBeenCalledWith('Portador adicionado', 'ok')
    })

    it('returns the created member', async () => {
      const newMember = makeMember({ id: 55, name: 'Pedro' })
      mockApiFetch.mockResolvedValue(newMember)

      const { createMember } = useMembers()
      const result = await createMember({ name: 'Pedro', relationship: 'dependente' })
      expect(result.id).toBe(55)
    })
  })

  describe('updateMember', () => {
    it('replaces the matching member in state', async () => {
      mockApiFetch.mockResolvedValueOnce([makeMember({ id: 1, name: 'Old Name' })])
      const updated = makeMember({ id: 1, name: 'New Name' })
      mockApiFetch.mockResolvedValueOnce(updated)

      const { members, fetchMembers, updateMember } = useMembers()
      await fetchMembers()
      await updateMember(1, { name: 'New Name' })

      expect(members.value[0].name).toBe('New Name')
    })

    it('shows success toast after update', async () => {
      mockApiFetch.mockResolvedValueOnce([makeMember({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(makeMember({ id: 1, name: 'Updated' }))

      const { fetchMembers, updateMember } = useMembers()
      await fetchMembers()
      await updateMember(1, { name: 'Updated' })

      expect(mockAddToast).toHaveBeenCalledWith('Portador atualizado', 'ok')
    })
  })

  describe('deleteMember', () => {
    it('removes the member from state', async () => {
      mockApiFetch.mockResolvedValueOnce([
        makeMember({ id: 1, name: 'Keep' }),
        makeMember({ id: 2, name: 'Delete Me' }),
      ])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { members, fetchMembers, deleteMember } = useMembers()
      await fetchMembers()
      await deleteMember(2)

      expect(members.value).toHaveLength(1)
      expect(members.value[0].id).toBe(1)
    })

    it('shows success toast after deletion', async () => {
      mockApiFetch.mockResolvedValueOnce([makeMember({ id: 1 })])
      mockApiFetch.mockResolvedValueOnce(undefined)

      const { fetchMembers, deleteMember } = useMembers()
      await fetchMembers()
      await deleteMember(1)

      expect(mockAddToast).toHaveBeenCalledWith('Portador removido', 'ok')
    })
  })
})
