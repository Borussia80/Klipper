<script setup lang="ts">
import type { Category } from '~/composables/useCategories'
import type { Account } from '~/composables/useAccounts'

const ModalNovoLancamento = defineAsyncComponent(() => import('~/components/ui/ModalNovoLancamento.vue'))
const ModalNovaConta = defineAsyncComponent(() => import('~/components/ui/ModalNovaConta.vue'))
const ModalNovoAporte = defineAsyncComponent(() => import('~/components/ui/ModalNovoAporte.vue'))
const ModalNovaCategoria = defineAsyncComponent(() => import('~/components/ui/ModalNovaCategoria.vue'))
const ModalNovoMembro = defineAsyncComponent(() => import('~/components/ui/ModalNovoMembro.vue'))
const ModalEditarReembolso = defineAsyncComponent(() => import('~/components/ui/ModalEditarReembolso.vue'))
const ModalEditarCartao = defineAsyncComponent(() => import('~/components/ui/ModalEditarCartao.vue'))

const { activeModal, modalPayload, close } = useModal()
</script>

<template>
  <ModalNovoLancamento :open="activeModal === 'novo-lancamento'" @close="close" />
  <ModalNovaConta :open="activeModal === 'nova-conta'" @close="close" />
  <ModalNovoAporte :open="activeModal === 'novo-aporte'" @close="close" />
  <ModalNovaCategoria :open="activeModal === 'nova-categoria'" @close="close" />
  <ModalNovoMembro :open="activeModal === 'novo-portador'" @close="close" />
  <ModalEditarReembolso
    :open="activeModal === 'editar-categoria'"
    :category="(modalPayload as Category | null)"
    @close="close"
  />
  <ModalEditarCartao
    :open="activeModal === 'editar-cartao'"
    :account="(modalPayload as Account | null)"
    @close="close"
  />
</template>
