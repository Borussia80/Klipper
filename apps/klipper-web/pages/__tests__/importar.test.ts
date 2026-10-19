/**
 * importar.vue — UR-2. A primeira importação real entrou com "Sem conta
 * vinculada" (o padrão do seletor) e deixou 345 transações sem origem: saldo
 * por conta e patrimônio nascem quebrados sem nenhum aviso. A conta de destino
 * passou a ser obrigatória, e quem ainda não tem nenhuma cadastra ali mesmo.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import type { VueWrapper } from '@vue/test-utils'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import Importar from '../importar.vue'

const mockOpen = vi.fn()
const mockAccounts = ref<{ id: number; name: string }[]>([])
const mockPreview = ref<unknown>(null)
const mockConfirmImport = vi.fn()

mockNuxtImport('useAccounts', () => () => ({
  accounts: mockAccounts,
  fetchAccounts: vi.fn(),
}))

mockNuxtImport('useMembers', () => () => ({
  members: ref([]),
  fetchMembers: vi.fn(),
}))

mockNuxtImport('useModal', () => () => ({
  activeModal: ref(null),
  modalPayload: ref(null),
  open: mockOpen,
  close: vi.fn(),
}))

mockNuxtImport('useImport', () => () => ({
  result: ref(null),
  preview: mockPreview,
  isLoading: ref(false),
  error: ref(null),
  uploadFile: vi.fn(),
  previewFile: vi.fn(),
  confirmImport: mockConfirmImport,
  reset: vi.fn(),
}))

let wrapper: VueWrapper | null = null

describe('importar.vue — conta de destino obrigatória', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAccounts.value = []
    mockPreview.value = null
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('não oferece mais importar sem conta vinculada', async () => {
    mockAccounts.value = [{ id: 1, name: 'Conta corrente' }]

    wrapper = await mountSuspended(Importar)

    const options = wrapper.findAll('#import-account option')
    expect(options.map((o) => o.text())).toEqual(['Selecione a conta', 'Conta corrente'])
    expect(options[0].attributes('disabled')).toBeDefined()
  })

  it('sem nenhuma conta cadastrada, explica o problema e abre o cadastro', async () => {
    wrapper = await mountSuspended(Importar)

    const aviso = wrapper.find('[data-testid="import-sem-conta"]')
    expect(aviso.exists()).toBe(true)
    expect(wrapper.find('#import-account').exists()).toBe(false)

    await aviso.find('button').trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('nova-conta')
  })

  it('com arquivo escolhido, o upload só libera depois da conta', async () => {
    mockAccounts.value = [{ id: 1, name: 'Conta corrente' }]

    wrapper = await mountSuspended(Importar)
    const vm = wrapper.vm as unknown as { selectedFile: File | null; selectedAccountId: number | undefined }
    vm.selectedFile = new File(['Data,Descrição,Valor'], 'extrato.csv', { type: 'text/csv' })
    await nextTick()

    const upload = () => wrapper!.findAll('button').find((b) => b.text().includes('Importar transações'))
    expect(upload()?.attributes('disabled')).toBeDefined()

    vm.selectedAccountId = 1
    await nextTick()

    expect(upload()?.attributes('disabled')).toBeUndefined()
  })

  it('pré-seleciona só a transferência pareada e confirma kind transfer sem alterar linha comum', async () => {
    mockPreview.value = {
      adapter: 'itau_extrato', warnings: [], rows: [
        { occurred_on: '2026-06-01', description: 'Transferência pareada', amount: '-10.00', installment_number: null, installment_total: null, page: 1, metadata: {}, token: 'a', own_transfer: { state: 'paired', counterpart: 'existing' } },
        { occurred_on: '2026-06-02', description: 'Compra comum', amount: '-20.00', installment_number: null, installment_total: null, page: 1, metadata: {}, token: 'b', own_transfer: null },
      ],
    }
    wrapper = await mountSuspended(Importar)
    await nextTick()

    expect(wrapper.text()).toContain('Transferência entre minhas contas')
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect((checkboxes[0].element as HTMLInputElement).checked).toBe(true)
    expect((checkboxes[1].element as HTMLInputElement).checked).toBe(true)
    expect((checkboxes[2].element as HTMLInputElement).checked).toBe(true)

    await wrapper.findAll('button').find((button) => button.text().includes('Confirmar importação'))!.trigger('click')
    expect(mockConfirmImport).toHaveBeenCalledWith([
      expect.objectContaining({ token: 'a', kind: 'transfer' }),
      expect.objectContaining({ token: 'b' }),
    ], undefined)
    expect(mockConfirmImport.mock.calls[0][0][1]).not.toHaveProperty('kind')
  })
})
