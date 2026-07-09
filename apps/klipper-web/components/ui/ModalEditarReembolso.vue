<template>
  <UiBaseModal
    title="Vínculo de reembolso"
    :subtitle="category ? `Editar reembolso de “${category.name}”` : undefined"
    :open="open"
    @close="$emit('close')"
  >
    <div>
      <label class="plbl">Reembolsada por</label>
      <div class="sel-wrap">
        <select v-model="reimbursedByCategoryId" class="fi fi-sel" aria-label="Categoria de receita que reembolsa esta despesa">
          <option :value="null">Nenhuma</option>
          <option v-for="inc in incomes" :key="inc.id" :value="inc.id">{{ inc.name }}</option>
        </select>
        <span class="sel-caret">▾</span>
      </div>
    </div>

    <div
      v-if="error"
      style="font-size:12px;color:var(--alert);margin-bottom:10px;padding:8px 12px;background:var(--ald);border-radius:var(--r)"
    >
      {{ error }}
    </div>

    <button
      class="btn btn-p"
      style="height:40px;width:100%;font-size:13px;font-weight:600"
      type="button"
      :disabled="isLoading || !category"
      @click="submit"
    >
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>Salvar</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
import type { Category } from '~/composables/useCategories'

const props = defineProps<{ open: boolean; category: Category | null }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { incomes, fetchCategories, updateCategory } = useCategories()

onMounted(() => fetchCategories())

const reimbursedByCategoryId = ref<number | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

watch(
  () => props.category,
  (category) => {
    reimbursedByCategoryId.value = category?.reimbursed_by_category_id ?? null
    error.value = null
  },
  { immediate: true },
)

async function submit() {
  if (!props.category) return
  isLoading.value = true
  error.value = null
  try {
    await updateCategory(props.category.id, { reimbursed_by_category_id: reimbursedByCategoryId.value })
    emit('close')
  } catch {
    addToast('Erro ao salvar. Tente novamente.', 'alert')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fi { margin-bottom: 16px; }
.fi-sel {
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
  padding-right: 32px;
}
.sel-wrap {
  position: relative;
}
.sel-caret {
  position: absolute;
  right: 11px;
  top: 50%;
  transform: translateY(-60%);
  color: var(--t3);
  font-size: 12px;
  pointer-events: none;
  line-height: 1;
  margin-bottom: 16px;
}
</style>
