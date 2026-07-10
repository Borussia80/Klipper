<template>
  <UiBaseModal
    title="Dados de dívida do cartão"
    :subtitle="account ? `Editar “${account.name}”` : undefined"
    :open="open"
    @close="$emit('close')"
  >
    <div>
      <label class="flbl">Saldo da fatura atual</label>
      <input
        v-model.number="saldoFaturaAtual"
        type="number"
        step="0.01"
        placeholder="0,00"
        class="fi"
        aria-label="Saldo da fatura atual"
      />
    </div>

    <div>
      <label class="flbl">Pagamento mínimo</label>
      <input
        v-model.number="pagamentoMinimo"
        type="number"
        step="0.01"
        placeholder="0,00"
        class="fi"
        aria-label="Pagamento mínimo da fatura"
      />
    </div>

    <div>
      <label class="flbl">Juros do rotativo (a.m.)</label>
      <input
        v-model.number="jurosRotativoAm"
        type="number"
        step="0.01"
        placeholder="Ex: 12,92"
        class="fi"
        aria-label="Juros do rotativo ao mês, em percentual"
      />
    </div>

    <div>
      <label class="flbl">Juros do rotativo (a.a.)</label>
      <input
        v-model.number="jurosRotativoAa"
        type="number"
        step="0.01"
        placeholder="Ex: 435,00"
        class="fi"
        aria-label="Juros do rotativo ao ano, em percentual"
      />
    </div>

    <div style="margin-bottom:24px">
      <label class="flbl">IOF projetado</label>
      <input
        v-model.number="iofProjetado"
        type="number"
        step="0.01"
        placeholder="0,00"
        class="fi"
        aria-label="IOF projetado, conforme estampado na fatura"
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
      :disabled="isLoading || !account"
      @click="submit"
    >
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>Salvar</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
import type { Account } from '~/composables/useAccounts'

const props = defineProps<{ open: boolean; account: Account | null }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { updateAccount } = useAccounts()

const saldoFaturaAtual = ref<number | null>(null)
const pagamentoMinimo = ref<number | null>(null)
const jurosRotativoAm = ref<number | null>(null)
const jurosRotativoAa = ref<number | null>(null)
const iofProjetado = ref<number | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

watch(
  () => props.account,
  (account) => {
    saldoFaturaAtual.value = account?.saldo_fatura_atual ? Number(account.saldo_fatura_atual) : null
    pagamentoMinimo.value = account?.pagamento_minimo ? Number(account.pagamento_minimo) : null
    jurosRotativoAm.value = account?.juros_rotativo_am ? Number(account.juros_rotativo_am) : null
    jurosRotativoAa.value = account?.juros_rotativo_aa ? Number(account.juros_rotativo_aa) : null
    iofProjetado.value = account?.iof_projetado ? Number(account.iof_projetado) : null
    error.value = null
  },
  { immediate: true },
)

async function submit() {
  if (!props.account) return
  isLoading.value = true
  error.value = null
  try {
    await updateAccount(props.account.id, {
      saldo_fatura_atual: saldoFaturaAtual.value?.toString() ?? null,
      pagamento_minimo: pagamentoMinimo.value?.toString() ?? null,
      juros_rotativo_am: jurosRotativoAm.value?.toString() ?? null,
      juros_rotativo_aa: jurosRotativoAa.value?.toString() ?? null,
      iof_projetado: iofProjetado.value?.toString() ?? null,
    })
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
</style>
