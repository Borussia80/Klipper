import type { BudgetSummaryRow } from './useBudgets'

export function sumAllocated(rows: BudgetSummaryRow[]): number {
  return rows.reduce((s, r) => s + Number(r.amount_limit), 0)
}

export function sumSpent(rows: BudgetSummaryRow[]): number {
  return rows.reduce((s, r) => s + Number(r.spent), 0)
}

export function freeAmount(allocated: number, spent: number): number {
  return allocated - spent
}

export function budgetSpentRatio(spent: number, allocated: number): number | null {
  if (allocated <= 0) return null
  return spent / allocated
}
