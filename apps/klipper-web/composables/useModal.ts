type ModalName = 'novo-lancamento' | 'nova-conta' | 'novo-aporte' | 'nova-categoria'

const activeModal = ref<ModalName | null>(null)

export function useModal() {
  function open(name: ModalName) { activeModal.value = name }
  function close() { activeModal.value = null }
  return { activeModal: readonly(activeModal), open, close }
}
