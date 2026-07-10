<template>
  <UiBaseModal
    title="Novo portador"
    subtitle="Cadastre quem usa suas contas e cartões"
    :open="open"
    @close="$emit('close')"
  >
    <div>
      <label class="flbl">Nome</label>
      <input
        v-model="nome"
        type="text"
        placeholder="Ex: Roberto Milet"
        class="fi"
        aria-label="Nome do portador"
      />
    </div>

    <div style="margin-bottom:24px">
      <label class="flbl">Relação</label>
      <div class="sel-wrap">
        <select v-model="relacao" class="fi fi-sel" aria-label="Relação do portador">
          <option value="titular">Titular</option>
          <option value="dependente">Dependente</option>
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
      :disabled="isLoading"
      @click="submit"
    >
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>Adicionar portador</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { createMember } = useMembers()

const nome = ref('')
const relacao = ref<'titular' | 'dependente'>('titular')
const isLoading = ref(false)
const error = ref<string | null>(null)

function validate(): string | null {
  if (!nome.value.trim()) return 'Informe o nome do portador'
  return null
}

async function submit() {
  error.value = validate()
  if (error.value) return
  isLoading.value = true
  try {
    await createMember({
      name: nome.value.trim(),
      relationship: relacao.value,
    })
    nome.value = ''
    relacao.value = 'titular'
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
