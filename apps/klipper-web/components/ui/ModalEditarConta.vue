<template>
  <UiBaseModal title="Editar conta" :open="open" @close="$emit('close')">
    <div>
      <label class="flbl">Nome</label>
      <input v-model="name" class="fi" type="text" aria-label="Nome da conta">
    </div>
    <div>
      <label class="flbl">Instituição</label>
      <input v-model="institution" class="fi" type="text" aria-label="Instituição financeira">
    </div>
    <div>
      <label class="flbl">Tipo</label>
      <select v-model="accountType" class="fi" aria-label="Tipo de conta">
        <option value="checking">Conta corrente</option>
        <option value="savings">Conta poupança</option>
        <option value="digital">Conta digital</option>
        <option value="investment">Conta investimento</option>
      </select>
    </div>
    <div style="margin-bottom:24px">
      <label class="flbl">Saldo</label>
      <input v-model="balance" class="fi" type="text" inputmode="decimal" aria-label="Saldo da conta">
    </div>
    <div v-if="error" role="alert" class="form-error">{{ error }}</div>
    <button class="btn btn-p" style="height:40px;width:100%" type="button" :disabled="isLoading" @click="submit">
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>Salvar conta</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
import type { Account } from '~/composables/useAccounts'

const props = defineProps<{ open: boolean; account: Account | null }>()
const emit = defineEmits<{ close: [] }>()
const { updateAccount } = useAccounts()
const name = ref('')
const institution = ref('')
const accountType = ref('checking')
const balance = ref('')
const error = ref<string | null>(null)
const isLoading = ref(false)

watch(() => props.account, (account: Account | null) => {
  if (!account) return
  name.value = account.name
  institution.value = account.institution ?? ''
  accountType.value = account.account_type
  balance.value = Number(account.balance).toString().replace('.', ',')
  error.value = null
}, { immediate: true })

async function submit() {
  if (!props.account) return
  const amount = parseBRLAmount(balance.value)
  if (!name.value.trim()) error.value = 'Informe o nome da conta'
  else if (amount === null) error.value = 'Informe um saldo válido'
  else error.value = null
  if (error.value) return
  isLoading.value = true
  try {
    await updateAccount(props.account.id, {
      name: name.value.trim(), institution: institution.value.trim() || null,
      account_type: accountType.value, balance: String(amount),
    })
    emit('close')
  } catch {
    error.value = 'Não foi possível salvar. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fi { margin-bottom:16px; }
.form-error { font-size:12px;color:var(--alert);margin-bottom:10px;padding:8px 12px;background:var(--ald);border-radius:var(--r); }
</style>
