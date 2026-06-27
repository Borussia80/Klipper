<script setup>
const ModalNovoLancamento = defineAsyncComponent(() => import('~/components/ui/ModalNovoLancamento.vue'))
const ModalNovaConta = defineAsyncComponent(() => import('~/components/ui/ModalNovaConta.vue'))
const ModalNovoAporte = defineAsyncComponent(() => import('~/components/ui/ModalNovoAporte.vue'))
const ModalNovaCategoria = defineAsyncComponent(() => import('~/components/ui/ModalNovaCategoria.vue'))

const { activeModal, close } = useModal()
</script>

<template>
  <ModalNovoLancamento :open="activeModal === 'novo-lancamento'" @close="close" />
  <ModalNovaConta :open="activeModal === 'nova-conta'" @close="close" />
  <ModalNovoAporte :open="activeModal === 'novo-aporte'" @close="close" />
  <ModalNovaCategoria :open="activeModal === 'nova-categoria'" @close="close" />
</template>
