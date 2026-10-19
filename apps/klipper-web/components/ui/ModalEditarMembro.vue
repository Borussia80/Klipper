<template>
  <UiBaseModal title="Editar portador" :open="open" @close="$emit('close')">
    <div style="margin-bottom:24px">
      <label class="flbl">Nome</label>
      <input v-model="name" class="fi" type="text" aria-label="Nome do portador">
    </div>
    <div v-if="error" role="alert" class="form-error">{{ error }}</div>
    <button class="btn btn-p" style="height:40px;width:100%" type="button" :disabled="isLoading" @click="submit">
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>Salvar portador</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
import type { Member } from '~/composables/useMembers'

const props = defineProps<{ open: boolean; member: Member | null }>()
const emit = defineEmits<{ close: [] }>()
const { updateMember } = useMembers()
const name = ref('')
const error = ref<string | null>(null)
const isLoading = ref(false)

watch(() => props.member, (member: Member | null) => {
  if (!member) return
  name.value = member.name
  error.value = null
}, { immediate: true })

async function submit() {
  if (!props.member) return
  if (!name.value.trim()) {
    error.value = 'Informe o nome do portador'
    return
  }
  isLoading.value = true
  error.value = null
  try {
    await updateMember(props.member.id, { name: name.value.trim() })
    emit('close')
  } catch {
    error.value = 'Não foi possível salvar. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fi { margin-bottom:0; }
.form-error { font-size:12px;color:var(--alert);margin-bottom:10px;padding:8px 12px;background:var(--ald);border-radius:var(--r); }
</style>
