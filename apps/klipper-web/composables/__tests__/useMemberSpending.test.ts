import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { toMemberSpendList } from '../useMemberSpending'
import type { MonthlyReport } from '../useReports'

function makeMonthly(overrides: Partial<MonthlyReport> = {}): MonthlyReport {
  return {
    year: 2026,
    month: 7,
    total_debits: 270.50,
    total_credits: 5000.00,
    net: 4729.50,
    by_category: [],
    ...overrides,
  }
}

describe('toMemberSpendList', () => {
  it('maps results to memberId/totalDebits pairs, preserving order', () => {
    const results = [
      { memberId: 2, report: makeMonthly({ total_debits: 132.00 }) },
      { memberId: 1, report: makeMonthly({ total_debits: 894.50 }) },
    ]
    expect(toMemberSpendList(results)).toEqual([
      { memberId: 2, totalDebits: 132.00 },
      { memberId: 1, totalDebits: 894.50 },
    ])
  })

  it('returns totalDebits 0 when the report is null', () => {
    const results = [{ memberId: 5, report: null }]
    expect(toMemberSpendList(results)).toEqual([{ memberId: 5, totalDebits: 0 }])
  })

  it('returns an empty array for an empty input', () => {
    expect(toMemberSpendList([])).toEqual([])
  })
})

const mockApiFetch = vi.fn()

mockNuxtImport('useApi', () => () => ({
  apiFetch: mockApiFetch,
  token: { value: 'test-token' },
}))

describe('fetchMemberSpends', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches one report per member and returns distinct totals with no cross-talk', async () => {
    mockApiFetch.mockImplementation(async (_url: string, opts: { query: { member_id: number } }) => {
      const totals: Record<number, number> = { 1: 894.50, 2: 132.00 }
      return makeMonthly({ total_debits: totals[opts.query.member_id] })
    })

    const { fetchMemberSpends } = await import('../useMemberSpending')
    const result = await fetchMemberSpends([1, 2], 2026, 7)

    expect(result).toEqual([
      { memberId: 1, totalDebits: 894.50 },
      { memberId: 2, totalDebits: 132.00 },
    ])
  })

  it('calls apiFetch once per member with year/month/member_id in the query', async () => {
    mockApiFetch.mockResolvedValue(makeMonthly())
    const { fetchMemberSpends } = await import('../useMemberSpending')
    await fetchMemberSpends([1, 2], 2026, 7)

    expect(mockApiFetch).toHaveBeenCalledTimes(2)
    expect(mockApiFetch).toHaveBeenCalledWith(
      '/api/v1/reports/monthly',
      expect.objectContaining({ query: { year: 2026, month: 7, member_id: 1 } }),
    )
    expect(mockApiFetch).toHaveBeenCalledWith(
      '/api/v1/reports/monthly',
      expect.objectContaining({ query: { year: 2026, month: 7, member_id: 2 } }),
    )
  })

  it('falls back to totalDebits 0 for a member whose fetch rejects, without throwing', async () => {
    mockApiFetch.mockImplementation(async (_url: string, opts: { query: { member_id: number } }) => {
      if (opts.query.member_id === 2) throw new Error('network error')
      return makeMonthly({ total_debits: 894.50 })
    })

    const { fetchMemberSpends } = await import('../useMemberSpending')
    const result = await fetchMemberSpends([1, 2], 2026, 7)

    expect(result).toEqual([
      { memberId: 1, totalDebits: 894.50 },
      { memberId: 2, totalDebits: 0 },
    ])
  })

  it('returns an empty array for an empty memberIds list', async () => {
    const { fetchMemberSpends } = await import('../useMemberSpending')
    const result = await fetchMemberSpends([], 2026, 7)
    expect(result).toEqual([])
    expect(mockApiFetch).not.toHaveBeenCalled()
  })
})
