import type { MonthlyReport } from './useReports'

export interface MemberSpend {
  memberId: number
  totalDebits: number
}

export function toMemberSpendList(
  results: { memberId: number; report: MonthlyReport | null }[],
): MemberSpend[] {
  return results.map((r) => ({ memberId: r.memberId, totalDebits: r.report?.total_debits ?? 0 }))
}

export async function fetchMemberSpends(
  memberIds: number[], year: number, month: number,
): Promise<MemberSpend[]> {
  const results = await Promise.all(
    memberIds.map(async (memberId) => {
      const { monthly, fetchMonthly } = useReports()
      await fetchMonthly(year, month, memberId)
      return { memberId, report: monthly.value }
    }),
  )
  return toMemberSpendList(results)
}
