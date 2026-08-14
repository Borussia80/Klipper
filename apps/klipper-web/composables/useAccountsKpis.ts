import type { Account } from './useAccounts'
import type { DebtRankingRow } from './useReports'

export function sumCheckingBalance(accounts: Account[]): number {
  return accounts
    .filter((a) => a.account_type !== 'credit_card')
    .reduce((sum, a) => sum + parseFloat(a.balance), 0)
}

export function sumDebtCharges(cards: DebtRankingRow[]): number {
  return cards.reduce((sum, c) => sum + c.encargos, 0)
}
