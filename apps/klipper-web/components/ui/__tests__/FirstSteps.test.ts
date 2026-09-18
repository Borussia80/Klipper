/**
 * FirstSteps.vue — UR-4. O usuário novo caía num painel vazio sem orientação:
 * a tela de onboarding existia mas nenhuma rota levava até ela. O bloco marca
 * cada etapa a partir do dado que já existe — conta, cartão, investimento e
 * orçamento — e nunca de um "concluído" guardado por conta própria.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import type { VueWrapper } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import type { Account } from '~/composables/useAccounts'
import type { Investment } from '~/composables/useInvestments'
import type { Budget } from '~/composables/useBudgets'
import FirstSteps from '../FirstSteps.vue'

const accounts = ref<Account[]>([])
const investments = ref<Investment[]>([])
const budgets = ref<Budget[]>([])
const oculto = ref<boolean | null>(null)
const mockOpen = vi.fn()

mockNuxtImport('useAccounts', () => () => ({ accounts, fetchAccounts: vi.fn() }))
mockNuxtImport('useInvestments', () => () => ({ investments, fetchInvestments: vi.fn() }))
mockNuxtImport('useBudgets', () => () => ({ budgets, fetchBudgets: vi.fn() }))
mockNuxtImport('useCookie', () => () => oculto)
mockNuxtImport('useModal', () => () => ({
  activeModal: ref(null),
  modalPayload: ref(null),
  open: mockOpen,
  close: vi.fn(),
}))

function account(type: string): Account {
  return { id: 1, name: 'Conta', account_type: type } as unknown as Account
}

let wrapper: VueWrapper | null = null

async function mountBlock() {
  wrapper = await mountSuspended(FirstSteps)
  await flushPromises()
  return wrapper
}

describe('FirstSteps.vue — primeiros passos do painel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    accounts.value = []
    investments.value = []
    budgets.value = []
    oculto.value = null
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('sem nada cadastrado, lista as quatro etapas e o progresso zerado', async () => {
    const block = await mountBlock()

    expect(block.findAll('li').map((i) => i.text())).toEqual([
      expect.stringContaining('Cadastrar a primeira conta'),
      expect.stringContaining('Cadastrar os cartões de crédito'),
      expect.stringContaining('Registrar a carteira de investimentos'),
      expect.stringContaining('Definir o primeiro objetivo financeiro'),
    ])
    expect(block.text()).toContain('0 de 4 concluídos · 0%')
    expect(block.get('[role="progressbar"]').attributes('aria-valuenow')).toBe('0')
  })

  it('marca as etapas pelos dados que já existem, sem estado próprio', async () => {
    accounts.value = [account('checking'), account('credit_card')]

    const block = await mountBlock()

    expect(block.text()).toContain('2 de 4 concluídos · 50%')
    expect(block.get('[role="progressbar"]').attributes('aria-valuenow')).toBe('50')
    expect(block.findAll('li.done').map((i) => i.text())).toEqual([
      expect.stringContaining('Cadastrar a primeira conta'),
      expect.stringContaining('Cadastrar os cartões de crédito'),
    ])
  })

  it('cada etapa pendente abre o modal correspondente', async () => {
    const block = await mountBlock()

    const cartao = block.findAll('button').find((b) => b.text() === 'Cadastrar cartão')
    await cartao!.trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('nova-conta', 'cartao')

    const objetivo = block.findAll('button').find((b) => b.text() === 'Definir objetivo')
    await objetivo!.trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('nova-categoria', null)
  })

  it('ocultar esconde o bloco e a escolha fica gravada', async () => {
    const block = await mountBlock()

    await block.get('button.fs-hide').trigger('click')

    expect(oculto.value).toBe(true)
    expect(block.find('section').exists()).toBe(false)
  })

  it('com as quatro etapas concluídas, não ocupa espaço no painel', async () => {
    accounts.value = [account('checking'), account('credit_card')]
    investments.value = [{ id: 1 } as unknown as Investment]
    budgets.value = [{ id: 1 } as unknown as Budget]

    const block = await mountBlock()

    expect(block.find('section').exists()).toBe(false)
  })
})
