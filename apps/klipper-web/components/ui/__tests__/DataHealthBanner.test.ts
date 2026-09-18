/**
 * DataHealthBanner — a faixa que explica por que as telas estão vazias.
 *
 * 338 de 345 transações importadas entraram sem categoria. Orçamento e
 * relatórios ficam vazios por consequência disso, mas o painel não dizia nada,
 * e o usuário conclui que o app não funciona. O número vai para a tela.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import type { VueWrapper } from '@vue/test-utils'
import DataHealthBanner from '../DataHealthBanner.vue'

const accounts = ref<{ id: number; name: string; account_type: string }[]>([])
const mockFetchAccounts = vi.fn()
const mockAssign = vi.fn(async () => 345)
const mockOpen = vi.fn()

mockNuxtImport('useAccounts', () => () => ({
  accounts,
  fetchAccounts: mockFetchAccounts,
}))

mockNuxtImport('useTransactions', () => () => ({
  assignAccountToOrphans: mockAssign,
}))

mockNuxtImport('useModal', () => () => ({
  open: mockOpen,
}))

describe('DataHealthBanner', () => {
  let wrapper: VueWrapper | undefined

  beforeEach(() => {
    vi.clearAllMocks()
    accounts.value = []
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('diz quantas transações estão sem categoria e o que isso custa', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 345, uncategorized: 338, without_account: 345 } },
    })

    expect(wrapper.text()).toContain('338 de 345')
    expect(wrapper.text()).toContain('orçamento')
    expect(wrapper.find('a[href="/transacoes"]').exists()).toBe(true)
  })

  it('some quando está tudo categorizado e todo lançamento tem conta', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 345, uncategorized: 0, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  // Base vazia é o estado do usuário novo: a faixa falaria de um problema que
  // ele ainda não tem.
  it('some quando não há transação nenhuma', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 0, uncategorized: 0, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  it('não desenha nada enquanto a contagem não chegou', async () => {
    wrapper = await mountSuspended(DataHealthBanner, { props: { health: null } })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  // Uma minoria sem categoria não justifica uma faixa de alerta no painel: o
  // aviso é para o caso em que a categorização é o que está travando as telas.
  it('não alarma quando a maior parte já está categorizada', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 345, uncategorized: 12, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health"]').exists()).toBe(false)
  })

  it('mostra a proporção como barra', async () => {
    wrapper = await mountSuspended(DataHealthBanner, {
      props: { health: { transactions: 100, uncategorized: 75, without_account: 0 } },
    })

    expect(wrapper.find('[data-testid="data-health-bar"]').attributes('style')).toContain('width: 75%')
  })

  describe('lançamentos sem conta', () => {
    const SEM_CONTA = { transactions: 345, uncategorized: 0, without_account: 345 }

    it('diz quantos estão sem conta e o que isso impede', async () => {
      wrapper = await mountSuspended(DataHealthBanner, { props: { health: SEM_CONTA } })

      const linha = wrapper.find('[data-testid="sem-conta"]')
      expect(linha.exists()).toBe(true)
      expect(linha.text()).toContain('345')
      expect(linha.text()).toContain('saldo')
    })

    // Na base real são zero contas cadastradas: não há o que escolher, e pedir
    // para escolher seria um beco sem saída.
    it('sem nenhuma conta cadastrada, manda cadastrar a conta primeiro', async () => {
      wrapper = await mountSuspended(DataHealthBanner, { props: { health: SEM_CONTA } })

      expect(wrapper.find('[data-testid="sem-conta-select"]').exists()).toBe(false)
      await wrapper.find('[data-testid="sem-conta-cta"]').trigger('click')

      expect(mockOpen).toHaveBeenCalledWith('nova-conta')
    })

    it('com contas cadastradas, oferece a escolha e liga os lançamentos', async () => {
      accounts.value = [
        { id: 7, name: 'Nubank – 1234', account_type: 'checking' },
        { id: 8, name: 'Itaú – 9999', account_type: 'checking' },
      ]

      wrapper = await mountSuspended(DataHealthBanner, { props: { health: SEM_CONTA } })

      const select = wrapper.find('[data-testid="sem-conta-select"]')
      expect(select.exists()).toBe(true)
      await select.setValue('8')
      await wrapper.find('[data-testid="sem-conta-cta"]').trigger('click')

      expect(mockAssign).toHaveBeenCalledWith(8)
    })

    it('avisa quem cuida da tela que a correção aconteceu', async () => {
      accounts.value = [{ id: 7, name: 'Nubank – 1234', account_type: 'checking' }]

      wrapper = await mountSuspended(DataHealthBanner, { props: { health: SEM_CONTA } })
      await wrapper.find('[data-testid="sem-conta-cta"]').trigger('click')
      await new Promise((r) => setTimeout(r, 0))

      expect(wrapper.emitted('corrigido')).toBeTruthy()
    })

    it('some quando todo lançamento já tem conta', async () => {
      wrapper = await mountSuspended(DataHealthBanner, {
        props: { health: { transactions: 345, uncategorized: 0, without_account: 0 } },
      })

      expect(wrapper.find('[data-testid="sem-conta"]').exists()).toBe(false)
    })
  })
})
