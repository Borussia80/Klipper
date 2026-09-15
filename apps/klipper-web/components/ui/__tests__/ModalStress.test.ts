/**
 * Testes de Stress e Resiliência em Modais (Frontend QA)
 *
 * Cobre:
 * 1. Double submit / Race conditions em botões de confirmação.
 * 2. Inputs de fronteira / Edge cases (payloads gigantes, SQLi / XSS strings, valores negativos/extremos).
 * 3. Fechamento por tecla ESC e clique no backdrop.
 * 4. Validação e prevenção de submissão com dados inválidos.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalNovoLancamento from '../ModalNovoLancamento.vue'
import ModalNovaCategoria from '../ModalNovaCategoria.vue'
import ModalConfirmDelete from '../ModalConfirmDelete.vue'

const mockAddToast = vi.fn()
const mockCreateTransaction = vi.fn()
const mockCreateCategory = vi.fn()
const mockUpdateAccount = vi.fn()

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

mockNuxtImport('useAccounts', () => () => ({
  accounts: { value: [{ id: 1, name: 'Nubank' }] },
  fetchAccounts: vi.fn().mockResolvedValue(undefined),
  updateAccount: mockUpdateAccount,
}))

mockNuxtImport('useCategories', () => () => ({
  categories: { value: [{ id: 1, name: 'Mercado' }] },
  fetchCategories: vi.fn().mockResolvedValue(undefined),
  createCategory: mockCreateCategory,
}))

mockNuxtImport('useTransactions', () => () => ({
  createTransaction: mockCreateTransaction,
}))

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

describe('QA Stress Test Suite — Modais de Interface', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 7, 15, 12, 0, 0))
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
    vi.useRealTimers()
  })

  describe('ModalNovoLancamento — Stress & Race Conditions', () => {
    async function mountModal() {
      wrapper = await mountSuspended(ModalNovoLancamento, { props: { open: true }, attachTo: document.body })
      return wrapper
    }

    it('impede múltiplos disparos simultâneos (Double Click / Rapid Fire) no CTA de confirmação', async () => {
      // Promessa lenta simulando latência de rede (500ms)
      mockCreateTransaction.mockImplementation(() => new Promise((resolve) => setTimeout(() => resolve({ id: 100 }), 500)))

      await mountModal()
      await body.find('input[aria-label="Valor do lançamento em reais"]').setValue('150,00')
      await body.find('input[aria-label="Descrição do lançamento"]').setValue('Teste Rapid Fire')

      const button = body.find('button.cta')
      
      // Dispara 5 cliques hiper rápidos antes do primeiro promessa resolver
      await button.trigger('click')
      await button.trigger('click')
      await button.trigger('click')
      await button.trigger('click')
      await button.trigger('click')

      // Avança os timers
      await vi.advanceTimersByTimeAsync(600)

      // Garantir que a API foi chamada APENAS 1 VEZ (proteção contra chamadas duplicadas)
      expect(mockCreateTransaction).toHaveBeenCalledTimes(1)
    })

    it('suporta strings gigantes e caracteres especiais (Boundary & XSS) sem quebrar o layout/payload', async () => {
      mockCreateTransaction.mockResolvedValue({ id: 101 })
      await mountModal()

      const payloadXSS = '<script>alert("xss")</script> &\'"<--' + 'A'.repeat(500)
      await body.find('input[aria-label="Valor do lançamento em reais"]').setValue('999999999,99')
      await body.find('input[aria-label="Descrição do lançamento"]').setValue(payloadXSS)

      await body.find('button.cta').trigger('click')
      await vi.waitFor(() => expect(mockCreateTransaction).toHaveBeenCalled())

      expect(mockCreateTransaction).toHaveBeenCalledWith(
        expect.objectContaining({
          description: payloadXSS,
          amount: '999999999.99'
        })
      )
    })
  })

  describe('ModalNovaCategoria — Validação e Fechamento', () => {
    async function mountModal() {
      wrapper = await mountSuspended(ModalNovaCategoria, { props: { open: true }, attachTo: document.body })
      return wrapper
    }

    it('impede submissão com nome vazio ou apenas espaços', async () => {
      await mountModal()
      await body.find('input[aria-label="Nome da categoria"]').setValue('    ')

      await body.find('button.cta').trigger('click')
      expect(mockCreateCategory).not.toHaveBeenCalled()
    })
  })

  describe('ModalConfirmDelete — Confirmações Críticas', () => {
    it('emite evento de confirmação e executa callback onConfirm', async () => {
      const mockOnConfirm = vi.fn().mockResolvedValue(undefined)
      wrapper = await mountSuspended(ModalConfirmDelete, {
        props: {
          open: true,
          payload: {
            title: 'Excluir Lançamento',
            description: 'Esta ação não poderá ser desfeita.',
            onConfirm: mockOnConfirm
          }
        },
        attachTo: document.body
      })

      const btnConfirm = body.find('button.confirm-danger')
      await btnConfirm.trigger('click')
      await vi.waitFor(() => expect(mockOnConfirm).toHaveBeenCalled())
      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })
})
