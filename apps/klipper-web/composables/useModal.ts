type ModalName = 'novo-lancamento' | 'nova-conta' | 'novo-aporte' | 'nova-categoria' | 'novo-portador' | 'editar-categoria' | 'editar-cartao'

const activeModal = ref<ModalName | null>(null)
const modalPayload = ref<unknown>(null)

export function useModal() {
  function open(name: ModalName, payload: unknown = null) {
    activeModal.value = name
    modalPayload.value = payload
  }
  function close() {
    activeModal.value = null
    modalPayload.value = null
  }
  return { activeModal: readonly(activeModal), modalPayload: readonly(modalPayload), open, close }
}
