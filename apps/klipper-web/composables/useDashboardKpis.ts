/**
 * useDashboardKpis — funções puras de transformação para o dashboard.
 * Extraídas de computeds soltos na página para ficarem testáveis.
 */
import type { Transaction } from './useTransactions'
import type { Category } from './useCategories'
import type { NaturezaSplitRow, DebtRankingReport } from './useReports'

const NATUREZA_LABELS: Record<NaturezaSplitRow['natureza'], string> = {
  fixo: 'Fixos (não negociável)',
  cartao_parcelamento: 'Cartões & parcelas',
  variavel: 'Variáveis',
}

export function pickIncomeHighlight(transactions: Transaction[], categories: Category[]): Transaction | null {
  const incomeCategoryIds = new Set(
    categories.filter((c) => c.category_type === 'income').map((c) => c.id)
  )
  const candidates = transactions.filter(
    (t) => t.transaction_type === 'credit' && t.category_id !== null && incomeCategoryIds.has(t.category_id)
  )
  if (!candidates.length) return null
  return candidates.reduce((max, t) => (parseFloat(t.amount) > parseFloat(max.amount) ? t : max))
}

export function pctOfIncome(total: number, income: number | null): number | null {
  if (income === null || income <= 0) return null
  return total / income
}

export interface NaturezaBar {
  name: string
  value: number
  pct: number
  color: string
}

export function mapNaturezaSplitToBars(
  rows: NaturezaSplitRow[],
  colors: Record<NaturezaSplitRow['natureza'], string>
): NaturezaBar[] {
  return rows.map((r) => ({
    name: NATUREZA_LABELS[r.natureza] ?? r.natureza,
    value: r.total,
    pct: r.pct,
    color: colors[r.natureza],
  }))
}

export function isDebtAlarmVisible(debtRanking: DebtRankingReport | null): boolean {
  return (debtRanking?.cards[0]?.encargos ?? 0) > 0
}
