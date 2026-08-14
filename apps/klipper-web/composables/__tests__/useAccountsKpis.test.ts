/**
 * useAccountsKpis tests — funções puras que orquestram contas.vue.
 * Sem chamadas de API: só transformação de dados já buscados.
 */
import { describe, it, expect } from 'vitest'
import { sumCheckingBalance, sumDebtCharges } from '../useAccountsKpis'
import type { Account } from '../useAccounts'
import type { DebtRankingRow } from '../useReports'

function makeAccount(overrides: Partial<Account> = {}): Account {
  return {
    id: 1,
    name: 'Conta Corrente',
    institution: 'Itaú',
    account_type: 'checking',
    balance: '1000.00',
    currency: 'BRL',
    active: true,
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
    saldo_fatura_atual: null,
    pagamento_minimo: null,
    juros_rotativo_am: null,
    juros_rotativo_aa: null,
    iof_projetado: null,
    saldo_atualizado_em: null,
    ...overrides,
  }
}

function makeDebtRow(overrides: Partial<DebtRankingRow> = {}): DebtRankingRow {
  return {
    account_id: 1,
    name: 'Itaú',
    institution: null,
    saldo_fatura_atual: 9603.9,
    pagamento_minimo: null,
    juros_rotativo_am: 12.9,
    juros_rotativo_aa: 338,
    iof_projetado: null,
    encargos: 1116.98,
    saldo_projetado_proximo_mes: 10781,
    saldo_atualizado_em: null,
    ...overrides,
  }
}

describe('sumCheckingBalance', () => {
  it('sums only accounts that are not credit cards', () => {
    const accounts = [
      makeAccount({ id: 1, account_type: 'checking', balance: '1500.50' }),
      makeAccount({ id: 2, account_type: 'savings', balance: '3200.00' }),
      makeAccount({ id: 3, account_type: 'credit_card', balance: '-800.00' }),
    ]
    expect(sumCheckingBalance(accounts)).toBeCloseTo(4700.5, 2)
  })

  it('returns 0 for an empty array', () => {
    expect(sumCheckingBalance([])).toBe(0)
  })

  it('returns 0 when every account is a credit card', () => {
    const accounts = [makeAccount({ account_type: 'credit_card', balance: '-500.00' })]
    expect(sumCheckingBalance(accounts)).toBe(0)
  })
})

describe('sumDebtCharges', () => {
  it('sums encargos across debt ranking rows', () => {
    const rows = [
      makeDebtRow({ account_id: 1, encargos: 1116.98 }),
      makeDebtRow({ account_id: 2, encargos: 240.5 }),
    ]
    expect(sumDebtCharges(rows)).toBeCloseTo(1357.48, 2)
  })

  it('returns 0 for an empty array', () => {
    expect(sumDebtCharges([])).toBe(0)
  })
})
