/**
 * ModalNovoAporte tests — trava a regressão P0.1 (compra/venda descartado no
 * payload) e P0.2 (data descartada no payload), e verifica que um erro do
 * backend (ex.: venda sem posição suficiente) é exibido sem fechar o modal
 * nem resetar os campos preenchidos.
 *
 * BaseModal renders through <Teleport to="body">, attach document.body query
 * through DOMWrapper, pattern in ModalNovoLancamento.test.ts.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { DOMWrapper, type VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ModalNovoAporte from '../ModalNovoAporte.vue'

const mockAddToast = vi.fn()
const mockCreateInvestment = vi.fn()

mockNuxtImport('useToast', () => () => ({
  addToast: mockAddToast,
  removeToast: vi.fn(),
  toasts: { value: [] },
}))

mockNuxtImport('useInvestments', () => () => ({
  createInvestment: mockCreateInvestment,
}))

let wrapper: VueWrapper | null = null
const body = new DOMWrapper(document.body)

async function mountModal() {
  wrapper = await mountSuspended(ModalNovoAporte, { props: { open: true }, attachTo: document.body })
  return wrapper
}

async function fillValidFields() {
  await body.find('input[aria-label="Ticker ou nome do ativo"]').setValue('IVVB11')
  await body.find('input[aria-label="Quantidade de cotas ou ações"]').setValue('10')
  await body.find('input[aria-label="Preço unitário em reais"]').setValue('100,00')
}

function findToggleButton(label: 'Compra' | 'Venda') {
  return body.findAll('button').find((b) => b.text() === label)!
}

describe('ModalNovoAporte', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 7, 15, 12, 0, 0)) // 15/08/2026, meio-dia local
    mockCreateInvestment.mockResolvedValue({ id: 1 })
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
    vi.useRealTimers()
  })

  it('pré-preenche a data com o dia local de hoje', async () => {
    await mountModal()
    const data = body.find('input[aria-label="Data da operação"]').element as HTMLInputElement
    expect(data.value).toBe('2026-08-15')
  })

  it('desabilita o CTA e não envia quando a data é futura', async () => {
    await mountModal()
    await fillValidFields()
    await body.find('input[aria-label="Data da operação"]').setValue('2026-08-16')

    const cta = body.find('button.cta').element as HTMLButtonElement
    expect(cta.disabled).toBe(true)

    await body.find('button.cta').trigger('click')
    expect(mockCreateInvestment).not.toHaveBeenCalled()
  })

  it('envia operation_type "buy" e a data escolhida ao registrar uma compra', async () => {
    const w = await mountModal()
    await fillValidFields()
    await body.find('input[aria-label="Data da operação"]').setValue('2026-08-10')

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockCreateInvestment).toHaveBeenCalled())

    expect(mockCreateInvestment).toHaveBeenCalledWith(
      expect.objectContaining({ operation_type: 'buy', occurred_on: '2026-08-10' }),
    )
    expect(w.emitted('close')).toBeTruthy()
  })

  it('envia operation_type "sell" ao alternar para venda', async () => {
    await mountModal()
    await fillValidFields()
    await findToggleButton('Venda').trigger('click')

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockCreateInvestment).toHaveBeenCalled())

    expect(mockCreateInvestment).toHaveBeenCalledWith(
      expect.objectContaining({ operation_type: 'sell' }),
    )
  })

  it('exibe a mensagem de erro do backend e mantém o modal aberto quando a venda é rejeitada', async () => {
    mockCreateInvestment.mockRejectedValue({
      data: { errors: ['Quantidade insuficiente para venda (posição atual: 0)'] },
    })
    const w = await mountModal()
    await fillValidFields()
    await findToggleButton('Venda').trigger('click')

    await body.find('button.cta').trigger('click')
    await vi.waitFor(() => expect(mockCreateInvestment).toHaveBeenCalled())

    expect(mockAddToast).toHaveBeenCalledWith(
      'Quantidade insuficiente para venda (posição atual: 0)',
      'alert',
    )
    expect(w.emitted('close')).toBeFalsy()
    const ativo = body.find('input[aria-label="Ticker ou nome do ativo"]').element as HTMLInputElement
    expect(ativo.value).toBe('IVVB11')
  })
})
