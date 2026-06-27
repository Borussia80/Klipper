<template>
  <UiBaseModal
    title="Nova conta"
    subtitle="Adicione uma instituição financeira"
    :open="open"
    @close="$emit('close')"
  >
    <div>
      <label class="plbl">Instituição</label>
      <input
        v-model="instituicao"
        type="text"
        placeholder="Ex: Nubank, Itaú, BTG…"
        class="fi"
        aria-label="Nome da instituição financeira"
      />
    </div>

    <div>
      <label class="plbl">Tipo</label>
      <div class="sel-wrap">
        <select v-model="tipo" class="fi fi-sel" aria-label="Tipo de conta">
          <option value="corrente">Conta corrente</option>
          <option value="poupanca">Conta poupança</option>
          <option value="digital">Conta digital</option>
          <option value="cartao">Cartão de crédito</option>
          <option value="investimento">Conta investimento</option>
        </select>
        <span class="sel-caret">▾</span>
      </div>
    </div>

    <div style="margin-bottom:24px">
      <label class="plbl">Identificador</label>
      <input
        v-model="identificador"
        type="text"
        placeholder="Últimos 4 dígitos ou apelido"
        class="fi"
        aria-label="Identificador da conta (últimos 4 dígitos ou apelido)"
      />
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
      <span v-else>Adicionar conta</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { createAccount } = useAccounts()

const ACCOUNT_TYPE_MAP: Record<string, string> = {
  corrente: 'checking',
  poupanca: 'savings',
  digital: 'digital',
  cartao: 'credit_card',
  investimento: 'investment',
}

const instituicao = ref('')
const tipo = ref('corrente')
const identificador = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)

function validate(): string | null {
  if (!instituicao.value.trim()) return 'Informe o nome da instituição'
  if (!identificador.value.trim()) return 'Informe um identificador para a conta'
  return null
}

async function submit() {
  error.value = validate()
  if (error.value) return
  isLoading.value = true
  try {
    const name = identificador.value.trim()
      ? `${instituicao.value.trim()} – ${identificador.value.trim()}`
      : instituicao.value.trim()
    await createAccount({
      name,
      institution: instituicao.value.trim(),
      account_type: ACCOUNT_TYPE_MAP[tipo.value] ?? 'checking',
      currency: 'BRL',
    })
    instituicao.value = ''
    identificador.value = ''
    tipo.value = 'corrente'
    emit('close')
  } catch {
    addToast('Erro ao salvar. Tente novamente.', 'alert')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fi {
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: var(--r);
  padding: 9px 12px;
  color: var(--t1);
  font-size: 13px;
  width: 100%;
  outline: none;
  font-family: inherit;
  transition: border-color .12s;
  margin-bottom: 16px;
  box-sizing: border-box;
}
.fi:focus {
  border-color: var(--blue);
}
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
