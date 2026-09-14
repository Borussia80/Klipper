/**
 * transacoes.vue — verifica que clicar numa linha de lançamento abre o modal
 * de edição (editar-lancamento) com a transação como payload, que o botão
 * de excluir (que já usa @click.stop) não dispara essa mesma abertura, e a
 * seleção em lote (achados de QA: seleção some ao trocar de filtro, exclusão
 * em lote roda em paralelo e sobrevive a falha parcial sem travar).
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import Transacoes from '../transacoes.vue'

const mockOpen = vi.fn()
const mockFetchTransactions = vi.fn()
const mockDeleteTransaction = vi.fn()
const mockAddToast = vi.fn()

const transaction = {
  id: 7,
  account_id: 1,
  category_id: 1,
  description: 'Mercado',
  amount: '50.00',
  transaction_type: 'debit',
  occurred_on: '2026-08-10',
  notes: null,
  installment_total: null,
  installment_number: null,
  member_id: null,
}

const transaction2 = {
  ...transaction,
  id: 8,
  description: 'Farmácia',
  amount: '30.00',
}

const mockTransactions = ref<typeof transaction[]>([transaction])

mockNuxtImport('useModal', () => () => ({
  activeModal: ref(null),
  modalPayload: ref(null),
  open: mockOpen,
  close: vi.fn(),
}))

mockNuxtImport('useTransactions', () => () => ({
  transactions: mockTransactions,
  isLoading: ref(false),
  fetchTransactions: mockFetchTransactions,
  deleteTransaction: mockDeleteTransaction,
}))

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

/** Captura o onConfirm passado pro modal de confirmação num dos chamados de `open('confirm-delete', ...)`. */
function lastConfirmDeleteCallback() {
  const call = mockOpen.mock.calls.findLast(([name]) => name === 'confirm-delete')
  return call?.[1].onConfirm as () => Promise<void>
}

describe('transacoes.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockTransactions.value = [transaction, transaction2]
    mockDeleteTransaction.mockResolvedValue(undefined)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('abre o modal de edição ao clicar na linha do lançamento', async () => {
    const wrapper = await mountSuspended(Transacoes)

    await wrapper.find('.txr').trigger('click')

    expect(mockOpen).toHaveBeenCalledWith('editar-lancamento', transaction)
  })

  it('não abre o modal de edição ao clicar em excluir', async () => {
    const wrapper = await mountSuspended(Transacoes)

    await wrapper.find('.tx-delete').trigger('click')

    expect(mockOpen).not.toHaveBeenCalledWith('editar-lancamento', expect.anything())
    expect(mockOpen).toHaveBeenCalledWith('confirm-delete', expect.anything())
  })

  it('mostra CTAs de ação no estado vazio e abre o modal de novo lançamento', async () => {
    mockTransactions.value = []
    const wrapper = await mountSuspended(Transacoes)

    expect(wrapper.text()).toContain('Nenhum lançamento no período.')

    await wrapper.find('button.btn-p').trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('novo-lancamento')

    const importLink = wrapper.findComponent({ name: 'NuxtLink' })
    expect(importLink.props('to')).toBe('/importar')
  })

  it('marca uma transação pelo checkbox e mostra a barra de ações em lote', async () => {
    const wrapper = await mountSuspended(Transacoes)
    expect(wrapper.find('.bulk-toolbar').exists()).toBe(false)

    await wrapper.find('.tx-checkbox').trigger('click')

    expect(wrapper.find('.bulk-toolbar').exists()).toBe(true)
    expect(wrapper.find('.bulk-count').text()).toContain('1 selecionada')
    // Marcar não deve abrir o modal de edição (o clique é @click.stop).
    expect(mockOpen).not.toHaveBeenCalledWith('editar-lancamento', expect.anything())
  })

  it('"Selecionar todas" marca todas as transações visíveis', async () => {
    const wrapper = await mountSuspended(Transacoes)
    await wrapper.find('.tx-checkbox').trigger('click')

    await wrapper.find('.bulk-link').trigger('click')

    expect(wrapper.find('.bulk-count').text()).toContain('2 selecionadas')
  })

  it('limpa a seleção ao trocar de filtro (linhas que somem não continuam marcadas)', async () => {
    const wrapper = await mountSuspended(Transacoes)
    await wrapper.find('.tx-checkbox').trigger('click')
    expect(wrapper.find('.bulk-toolbar').exists()).toBe(true)

    // O filtro começa em "Todos" — precisa mudar de fato pro watch disparar.
    await wrapper.findAll('button.pill')[1].trigger('click') // "Entradas"

    expect(wrapper.find('.bulk-toolbar').exists()).toBe(false)
  })

  it('exclui em lote em paralelo (Promise.allSettled) e some com toast de resumo', async () => {
    const wrapper = await mountSuspended(Transacoes)
    await wrapper.find('.tx-checkbox').trigger('click')
    const checkboxes = wrapper.findAll('.tx-checkbox')
    await checkboxes[1].trigger('click')

    await wrapper.findAll('.btn.btn-g')
      .find((b) => b.text().includes('Excluir selecionadas'))!
      .trigger('click')

    const onConfirm = lastConfirmDeleteCallback()
    await onConfirm()

    expect(mockDeleteTransaction).toHaveBeenCalledWith(7, { silent: true })
    expect(mockDeleteTransaction).toHaveBeenCalledWith(8, { silent: true })
    expect(mockAddToast).toHaveBeenCalledWith('2 lançamentos removidos', 'ok')
  })

  it('mantém selecionados só os que falharam, quando a exclusão em lote falha parcialmente', async () => {
    mockDeleteTransaction.mockImplementation((id: number) =>
      id === 8 ? Promise.reject(new Error('network error')) : Promise.resolve(undefined),
    )

    const wrapper = await mountSuspended(Transacoes)
    await wrapper.find('.tx-checkbox').trigger('click')
    const checkboxes = wrapper.findAll('.tx-checkbox')
    await checkboxes[1].trigger('click')

    await wrapper.findAll('.btn.btn-g')
      .find((b) => b.text().includes('Excluir selecionadas'))!
      .trigger('click')

    const onConfirm = lastConfirmDeleteCallback()
    await onConfirm()
    await wrapper.vm.$nextTick()

    expect(mockAddToast).toHaveBeenCalledWith('1 lançamento removido', 'ok')
    expect(mockAddToast).toHaveBeenCalledWith('Não foi possível excluir 1 lançamento.', 'alert')
    // Só o que falhou (id 8) continua selecionado — dá pra tentar excluir de novo.
    expect(wrapper.find('.bulk-count').text()).toContain('1 selecionada')
  })

  it('alterna entre visualização compacta e confortável', async () => {
    const wrapper = await mountSuspended(Transacoes)
    const toggle = wrapper.find('button[aria-label="Visualização compacta"]')
    expect(toggle.exists()).toBe(true)

    await toggle.trigger('click')

    expect(wrapper.find('button[aria-label="Visualização confortável"]').exists()).toBe(true)
    expect(wrapper.find('.txr.is-compact').exists()).toBe(true)
  })
})
