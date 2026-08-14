/**
 * useDashboardKpis tests — funções puras que orquestram o dashboard.
 * Sem chamadas de API: só transformação de dados já buscados.
 */
import { describe, it, expect } from 'vitest'
import {
  pickIncomeHighlight,
  pctOfIncome,
  mapNaturezaSplitToBars,
  isDebtAlarmVisible,
} from '../useDashboardKpis'
import type { Transaction } from '../useTransactions'
import type { Category } from '../useCategories'
import type { NaturezaSplitRow, DebtRankingReport } from '../useReports'

function makeTransaction(overrides: Partial<Transaction> = {}): Transaction {
  return {
    id: 1,
    account_id: 1,
    category_id: null,
    description: 'Salário',
    amount: '5000.00',
    transaction_type: 'credit',
    occurred_on: '2026-07-05',
    notes: null,
    installment_total: null,
    installment_number: null,
    member_id: null,
    ...overrides,
  }
}

function makeCategory(overrides: Partial<Category> = {}): Category {
  return {
    id: 1,
    name: 'Salário',
    icon: 'income',
    category_type: 'income',
    natureza: 'fixo',
    color: null,
    active: true,
    reimbursed_by_category_id: null,
    ...overrides,
  }
}

describe('pickIncomeHighlight', () => {
  it('returns the largest credit transaction with an income category', () => {
    const categories = [makeCategory({ id: 1, category_type: 'income' })]
    const transactions = [
      makeTransaction({ id: 1, category_id: 1, amount: '5000.00' }),
      makeTransaction({ id: 2, category_id: 1, amount: '12604.00' }),
    ]
    const result = pickIncomeHighlight(transactions, categories)
    expect(result?.id).toBe(2)
  })

  it('ignores credits whose category is not income', () => {
    const categories = [makeCategory({ id: 1, category_type: 'expense' })]
    const transactions = [makeTransaction({ id: 1, category_id: 1, amount: '5000.00' })]
    expect(pickIncomeHighlight(transactions, categories)).toBeNull()
  })

  it('ignores debit transactions even with an income category', () => {
    const categories = [makeCategory({ id: 1, category_type: 'income' })]
    const transactions = [
      makeTransaction({ id: 1, category_id: 1, amount: '5000.00', transaction_type: 'debit' }),
    ]
    expect(pickIncomeHighlight(transactions, categories)).toBeNull()
  })

  it('ignores transactions without a category_id', () => {
    const categories = [makeCategory({ id: 1, category_type: 'income' })]
    const transactions = [makeTransaction({ id: 1, category_id: null, amount: '5000.00' })]
    expect(pickIncomeHighlight(transactions, categories)).toBeNull()
  })

  it('returns null when there are no transactions', () => {
    expect(pickIncomeHighlight([], [])).toBeNull()
  })
})

describe('pctOfIncome', () => {
  it('divides total by income', () => {
    expect(pctOfIncome(8132, 12604)).toBeCloseTo(0.6452, 3)
  })

  it('returns null when income is zero', () => {
    expect(pctOfIncome(100, 0)).toBeNull()
  })

  it('returns null when income is negative', () => {
    expect(pctOfIncome(100, -50)).toBeNull()
  })

  it('returns null when income is null', () => {
    expect(pctOfIncome(100, null)).toBeNull()
  })
})

describe('mapNaturezaSplitToBars', () => {
  const colors = { fixo: 'var(--sea)', cartao_parcelamento: 'var(--alert)', variavel: 'var(--brass)' }

  it('maps each row to a bar with its category color', () => {
    const rows: NaturezaSplitRow[] = [
      { natureza: 'fixo', total: 8132, pct: 35 },
      { natureza: 'cartao_parcelamento', total: 9874, pct: 43 },
      { natureza: 'variavel', total: 4910, pct: 21 },
    ]
    const bars = mapNaturezaSplitToBars(rows, colors)
    expect(bars).toHaveLength(3)
    expect(bars[0]).toEqual({ name: 'Fixos (não negociável)', value: 8132, pct: 35, color: 'var(--sea)' })
    expect(bars[1]).toEqual({ name: 'Cartões & parcelas', value: 9874, pct: 43, color: 'var(--alert)' })
    expect(bars[2]).toEqual({ name: 'Variáveis', value: 4910, pct: 21, color: 'var(--brass)' })
  })

  it('returns an empty array for an empty input', () => {
    expect(mapNaturezaSplitToBars([], colors)).toEqual([])
  })
})

describe('isDebtAlarmVisible', () => {
  function makeDebtRanking(overrides: Partial<DebtRankingReport> = {}): DebtRankingReport {
    return { cards: [], ...overrides }
  }

  it('is true when the top-ranked card has charges', () => {
    const report = makeDebtRanking({
      cards: [{
        account_id: 1, name: 'Itaú', institution: null, saldo_fatura_atual: 9603.9,
        pagamento_minimo: null, juros_rotativo_am: 12.9, juros_rotativo_aa: 338,
        iof_projetado: null, encargos: 1116.98, saldo_projetado_proximo_mes: 10781,
        saldo_atualizado_em: null,
      }],
    })
    expect(isDebtAlarmVisible(report)).toBe(true)
  })

  it('is false when the top-ranked card has zero charges', () => {
    const report = makeDebtRanking({
      cards: [{
        account_id: 1, name: 'Santander', institution: null, saldo_fatura_atual: 1029,
        pagamento_minimo: null, juros_rotativo_am: 0, juros_rotativo_aa: null,
        iof_projetado: null, encargos: 0, saldo_projetado_proximo_mes: 1029,
        saldo_atualizado_em: null,
      }],
    })
    expect(isDebtAlarmVisible(report)).toBe(false)
  })

  it('is false when there are no cards', () => {
    expect(isDebtAlarmVisible(makeDebtRanking())).toBe(false)
  })

  it('is false when the report is null', () => {
    expect(isDebtAlarmVisible(null)).toBe(false)
  })
})
