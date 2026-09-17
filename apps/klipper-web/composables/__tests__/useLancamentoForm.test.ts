/**
 * useLancamentoForm tests — o estado compartilhado pelos modais de Novo e de
 * Editar lançamento. O motivo de existir do composable é impedir que os dois
 * formulários divirjam, então o que precisa de teste é justamente o que os dois
 * herdam dele: a validação, o payload que vai para a API e o caminho de volta
 * (`fillFrom`), que reformata o valor numérico em texto BR e tem que voltar ao
 * mesmo número quando o formulário é submetido sem edição.
 */
import { describe, it, expect, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import { txTypeToTipo, useLancamentoForm } from '../useLancamentoForm'
import type { Transaction } from '../useTransactions'

mockNuxtImport('useAccounts', () => () => ({
  accounts: { value: [{ id: 1, name: 'Nubank' }] },
  fetchAccounts: vi.fn(),
}))

mockNuxtImport('useCategories', () => () => ({
  categories: { value: [{ id: 7, name: 'Mercado' }] },
  fetchCategories: vi.fn(),
}))

type Form = ReturnType<typeof useLancamentoForm>

async function mountForm(): Promise<Form> {
  let form!: Form
  await mountSuspended(defineComponent({
    setup() {
      form = useLancamentoForm()
      return () => h('div')
    },
  }))
  return form
}

// Espelha o todayISO() do composable: dia do calendário local, não UTC. Usar
// toISOString() aqui faria o teste virar de dia perto da meia-noite em BRT.
function isoDaysFromToday(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function makeTransaction(overrides: Partial<Transaction> = {}): Transaction {
  return {
    id: 1,
    account_id: 1,
    category_id: 7,
    description: 'Supermercado',
    amount: '1234.5',
    transaction_type: 'debit',
    occurred_on: '2026-09-10',
    ...overrides,
  } as Transaction
}

async function fillValid(form: Form) {
  form.valor.value = '50,00'
  form.descricao.value = 'Supermercado'
  form.conta.value = 1
}

describe('txTypeToTipo', () => {
  it('maps the API transaction_type onto the form tipo', () => {
    expect(txTypeToTipo('credit')).toBe('receita')
    expect(txTypeToTipo('transfer')).toBe('transferencia')
    expect(txTypeToTipo('debit')).toBe('gasto')
  })
})

describe('validate', () => {
  it('rejects an amount that does not parse', async () => {
    const form = await mountForm()
    await fillValid(form)
    // Formato americano com milhar: parseBRLAmount devolve null de propósito em
    // vez de adivinhar, e o formulário tem que barrar em vez de mandar "null".
    form.valor.value = '1,234.56'

    expect(form.validate()).toBe('Informe um valor válido')
    expect(form.isValid.value).toBe(false)
  })

  it('rejects zero and negative amounts', async () => {
    const form = await mountForm()
    await fillValid(form)

    form.valor.value = '0,00'
    expect(form.validate()).toBe('Informe um valor válido')

    form.valor.value = '-50,00'
    expect(form.validate()).toBe('Informe um valor válido')
  })

  it('rejects a description made only of whitespace', async () => {
    const form = await mountForm()
    await fillValid(form)
    form.descricao.value = '   '

    expect(form.validate()).toBe('Informe uma descrição')
  })

  it('rejects a future date', async () => {
    const form = await mountForm()
    await fillValid(form)
    form.data.value = isoDaysFromToday(1)

    expect(form.validate()).toBe('A data não pode ser futura')
  })

  it('accepts today, which is the default', async () => {
    const form = await mountForm()
    await fillValid(form)

    expect(form.data.value).toBe(isoDaysFromToday(0))
    expect(form.validate()).toBeNull()
    expect(form.isValid.value).toBe(true)
  })
})

describe('buildPayload', () => {
  it('sends the amount as a plain decimal string and trims the description', async () => {
    const form = await mountForm()
    form.valor.value = '1.234,56'
    form.descricao.value = '  Supermercado  '
    form.conta.value = 1
    form.categoria.value = 7

    expect(form.buildPayload()).toEqual({
      account_id: 1,
      category_id: 7,
      description: 'Supermercado',
      amount: '1234.56',
      transaction_type: 'debit',
      occurred_on: isoDaysFromToday(0),
    })
  })

  it('maps each tipo onto the transaction_type the API expects', async () => {
    const form = await mountForm()
    await fillValid(form)

    form.tipo.value = 'receita'
    expect(form.buildPayload().transaction_type).toBe('credit')

    form.tipo.value = 'transferencia'
    expect(form.buildPayload().transaction_type).toBe('transfer')

    form.tipo.value = 'gasto'
    expect(form.buildPayload().transaction_type).toBe('debit')
  })

  it('sends no account_id when none was chosen, and a null category as null', async () => {
    const form = await mountForm()
    await fillValid(form)
    form.conta.value = null
    form.categoria.value = null

    const payload = form.buildPayload()
    expect(payload.account_id).toBeUndefined()
    // Distinto de undefined de propósito: null é o que apaga a categoria na
    // edição, e foi essa diferença que já parou de funcionar num dos modais.
    expect(payload.category_id).toBeNull()
  })
})

describe('fillFrom', () => {
  it('loads a transaction into the form and clears a previous error', async () => {
    const form = await mountForm()
    form.error.value = 'erro anterior'

    form.fillFrom(makeTransaction({ transaction_type: 'credit', description: 'Salário' }))

    expect(form.tipo.value).toBe('receita')
    expect(form.descricao.value).toBe('Salário')
    expect(form.categoria.value).toBe(7)
    expect(form.conta.value).toBe(1)
    expect(form.data.value).toBe('2026-09-10')
    expect(form.error.value).toBeNull()
  })

  it('writes the amount in the BR format the input expects, with two decimals', async () => {
    const form = await mountForm()

    form.fillFrom(makeTransaction({ amount: '1234.5' }))

    expect(form.valor.value).toBe('1234,50')
  })

  it('round-trips the amount back to the same value when submitted unedited', async () => {
    const form = await mountForm()

    // O caminho de volta é onde um formato divergente passa despercebido: o
    // fillFrom escreve texto, o buildPayload reparseia, e se os dois não
    // concordarem a edição salva um valor diferente do que abriu na tela.
    for (const amount of ['1234.5', '0.99', '1234567.89', '38.50']) {
      form.fillFrom(makeTransaction({ amount }))

      expect(form.buildPayload().amount).toBe(String(Number(amount)))
    }
  })
})
