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
  preview: ref(null),
  isLoading: ref(false),
  error: ref(null),
  uploadFile: vi.fn(),
  previewFile: vi.fn(),
  confirmImport: vi.fn(),
  reset: vi.fn(),
}))

let wrapper: VueWrapper | null = null

describe('importar.vue — conta de destino obrigatória', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAccounts.value = []
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
})
