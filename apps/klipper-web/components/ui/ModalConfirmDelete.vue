<template>
  <UiBaseModal
    :title="payload?.title ?? 'Confirmar exclusão'"
    :subtitle="payload?.resourceType ? `Excluir ${payload.resourceType}` : undefined"
    :open="open"
    @close="handleCancel"
  >
    <div class="confirm-panel">
      <div class="confirm-icon" aria-hidden="true">
        <UiAppIcon name="alert" :size="18" />
      </div>
      <div>
        <p class="confirm-description">
          {{ payload?.description ?? 'Esta ação remove o item selecionado e não pode ser desfeita.' }}
        </p>
        <p v-if="payload?.itemName" class="confirm-item">
          {{ payload.itemName }}
        </p>
      </div>
    </div>

    <div v-if="error" class="confirm-error" role="alert">
      {{ error }}
    </div>

    <div class="confirm-actions">
      <button class="btn btn-g" type="button" :disabled="isLoading" @click="handleCancel">
        Cancelar
      </button>
      <button class="btn confirm-danger" type="button" :disabled="isLoading" @click="handleConfirm">
        <span v-if="isLoading" class="btn-spinner" />
        <span v-else>{{ payload?.confirmLabel ?? 'Excluir' }}</span>
      </button>
    </div>
  </UiBaseModal>
</template>

<script setup lang="ts">
import type { ConfirmDeletePayload } from '~/composables/useModal'

const props = defineProps<{
  open: boolean
  payload: ConfirmDeletePayload | null
}>()

const emit = defineEmits<{ close: [] }>()

const isLoading = ref(false)
const error = ref<string | null>(null)

watch(
  () => props.open,
  () => {
    error.value = null
    isLoading.value = false
  },
)

function handleCancel() {
  if (isLoading.value) return
  emit('close')
}

async function handleConfirm() {
  if (!props.payload?.onConfirm) return
  isLoading.value = true
  error.value = null
  try {
    await props.payload.onConfirm()
    emit('close')
  } catch {
    error.value = 'Não foi possível excluir. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.confirm-panel {
  display: grid;
  grid-template-columns: 38px 1fr;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(232, 115, 90, 0.34);
  border-radius: 10px;
  background: var(--ald);
  margin-bottom: 18px;
}

.confirm-icon {
  width: 38px;
  height: 38px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--alert);
  background: rgba(232, 115, 90, 0.14);
  border: 1px solid rgba(232, 115, 90, 0.28);
}

.confirm-description {
  font-size: 13px;
  line-height: 1.45;
  color: var(--t2);
}

.confirm-item {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--t1);
  overflow-wrap: anywhere;
}

.confirm-error {
  font-size: 12px;
  color: var(--alert);
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--ald);
  border: 1px solid rgba(232, 115, 90, 0.32);
  border-radius: var(--r);
}

.confirm-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.confirm-actions .btn {
  height: 40px;
  width: 100%;
  font-size: 13px;
  font-weight: 600;
}

.confirm-danger {
  background: var(--alert);
  color: #160907;
}

.confirm-danger:hover {
  background: #f08a72;
}
</style>
