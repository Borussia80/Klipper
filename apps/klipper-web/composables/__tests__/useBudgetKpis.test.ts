/**
 * useBudgetKpis tests — funções puras que orquestram orcamento.vue.
 * Sem chamadas de API: só transformação de dados já buscados.
 */
import { describe, it, expect } from 'vitest'
import { sumAllocated, sumSpent, freeAmount, budgetSpentRatio } from '../useBudgetKpis'
import type { BudgetSummaryRow } from '../useBudgets'

function makeRow(overrides: Partial<BudgetSummaryRow> = {}): BudgetSummaryRow {
  return {
    budget_id: 1,
    category_id: 1,
    category_name: 'Mercado',
    category_icon: 'cart',
    natureza: 'variavel',
    amount_limit: 1000,
    spent: 600,
    remaining: 400,
    pct_used: 60,
    recorrencia: 'rotineiro',
    months_present: 3,
    months_total: 3,
    ...overrides,
  }
}

describe('sumAllocated', () => {
  it('sums amount_limit across rows', () => {
    const rows = [makeRow({ amount_limit: 1000 }), makeRow({ amount_limit: 2500 })]
    expect(sumAllocated(rows)).toBe(3500)
  })

  it('returns 0 for an empty array', () => {
    expect(sumAllocated([])).toBe(0)
  })
})

describe('sumSpent', () => {
  it('sums spent across rows', () => {
    const rows = [makeRow({ spent: 600 }), makeRow({ spent: 132 })]
    expect(sumSpent(rows)).toBe(732)
  })

  it('returns 0 for an empty array', () => {
    expect(sumSpent([])).toBe(0)
  })
})

describe('freeAmount', () => {
  it('subtracts spent from allocated', () => {
    expect(freeAmount(10000, 8132)).toBe(1868)
  })

  it('can be negative when spent exceeds allocated', () => {
    expect(freeAmount(10000, 12000)).toBe(-2000)
  })
})

describe('budgetSpentRatio', () => {
  it('divides spent by allocated', () => {
    expect(budgetSpentRatio(8132, 10000)).toBeCloseTo(0.8132, 4)
  })

  it('can exceed 1 when over budget, without clamping', () => {
    expect(budgetSpentRatio(12000, 10000)).toBeCloseTo(1.2, 4)
  })

  it('returns null when allocated is zero', () => {
    expect(budgetSpentRatio(100, 0)).toBeNull()
  })

  it('returns null when allocated is negative', () => {
    expect(budgetSpentRatio(100, -50)).toBeNull()
  })
})
