<script setup lang="ts">
import type { Category } from '~/composables/useCategories'
import type { Account } from '~/composables/useAccounts'
import type { Transaction } from '~/composables/useTransactions'

const ModalNovoLancamento = defineAsyncComponent(() => import('~/components/ui/ModalNovoLancamento.vue'))
const ModalEditarLancamento = defineAsyncComponent(() => import('~/components/ui/ModalEditarLancamento.vue'))
const ModalNovaConta = defineAsyncComponent(() => import('~/components/ui/ModalNovaConta.vue'))
const ModalNovoAporte = defineAsyncComponent(() => import('~/components/ui/ModalNovoAporte.vue'))
const ModalNovaCategoria = defineAsyncComponent(() => import('~/components/ui/ModalNovaCategoria.vue'))
const ModalNovoMembro = defineAsyncComponent(() => import('~/components/ui/ModalNovoMembro.vue'))
const ModalEditarReembolso = defineAsyncComponent(() => import('~/components/ui/ModalEditarReembolso.vue'))
const ModalEditarCartao = defineAsyncComponent(() => import('~/components/ui/ModalEditarCartao.vue'))
const ModalConfirmDelete = defineAsyncComponent(() => import('~/components/ui/ModalConfirmDelete.vue'))
const CommandPalette = defineAsyncComponent(() => import('~/components/ui/CommandPalette.vue'))

const { activeModal, modalPayload, close } = useModal()
</script>

<template>
  <CommandPalette :open="activeModal === 'command-palette'" @close="close" />
  <ModalNovoLancamento :open="activeModal === 'novo-lancamento'" @close="close" />
  <ModalEditarLancamento
    :open="activeModal === 'editar-lancamento'"
    :transaction="(modalPayload as Transaction | null)"
    @close="close"
  />
  <ModalNovaConta
    :open="activeModal === 'nova-conta'"
    :preset-tipo="(modalPayload as string | null)"
    @close="close"
  />
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
  <ModalConfirmDelete
    :open="activeModal === 'confirm-delete'"
    :payload="(modalPayload as import('~/composables/useModal').ConfirmDeletePayload | null)"
    @close="close"
  />
</template>
