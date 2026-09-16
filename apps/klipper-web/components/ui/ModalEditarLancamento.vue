<template>
  <UiBaseModal
    title="Editar lançamento"
    :subtitle="transaction ? transaction.description : undefined"
    :open="open"
    @close="$emit('close')"
  >

    <!-- Type toggle -->
    <div class="tipo-toggle">
      <button
        v-for="opt in tipoOpcoes"
        :key="opt.value"
        class="tipo-btn"
        :class="{ active: tipo === opt.value }"
        type="button"
        :aria-pressed="tipo === opt.value"
        @click="tipo = opt.value"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Valor -->
    <p class="flbl">Valor</p>
    <div class="valor-wrap" :class="{ receita: tipo === 'receita' }">
      <span class="valor-prefix">R$</span>
      <input
        v-model="valor"
        class="valor-input"
        :class="{ receita: tipo === 'receita' }"
        type="text"
        inputmode="decimal"
        placeholder="0,00"
        aria-label="Valor do lançamento em reais"
      />
    </div>

    <!-- Descrição -->
    <p class="flbl">Descrição</p>
    <input
      v-model="descricao"
      class="field"
      type="text"
      placeholder="Ex: Supermercado Extra"
      style="margin-bottom:16px"
      aria-label="Descrição do lançamento"
    />

    <!-- Detalhes: categoria + conta + data -->
    <div class="gh" style="padding-top:6px">
      <span class="gl">Detalhes</span>
      <span class="gr"></span>
    </div>

    <div v-if="isLoadingData" class="row-two" style="margin-bottom:16px">
      <UiSkeletonLine height="34px" />
      <UiSkeletonLine height="34px" />
    </div>
    <div v-else class="row-two">
      <div>
        <p class="flbl">Categoria</p>
        <div class="select-wrap">
          <select v-model="categoria" class="field select" aria-label="Categoria do lançamento">
            <option :value="null">Sem categoria</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <span class="select-arrow">▾</span>
        </div>
      </div>

      <div>
        <p class="flbl">Conta</p>
        <div class="select-wrap">
          <select v-model="conta" class="field select" aria-label="Conta de origem">
            <option :value="null">Selecionar conta</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
          </select>
          <span class="select-arrow">▾</span>
        </div>
      </div>
    </div>

    <!-- Data -->
    <p class="flbl">Data</p>
    <input
      v-model="data"
      class="field"
      type="date"
      style="margin-bottom:24px"
      aria-label="Data do lançamento"
    />

    <!-- Validation error -->
    <div
      v-if="error"
      style="font-size:12px;color:var(--alert);margin-bottom:10px;padding:8px 12px;background:var(--ald);border-radius:var(--r)"
    >
      {{ error }}
    </div>

    <!-- CTA -->
    <button
      class="btn btn-p cta"
      type="button"
      :disabled="isLoading || !isValid || !transaction"
      @click="submit"
    >
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>Salvar</span>
    </button>

  </UiBaseModal>
</template>

<script setup lang="ts">
import type { Transaction } from '~/composables/useTransactions'

const props = defineProps<{ open: boolean; transaction: Transaction | null }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { updateTransaction } = useTransactions()
const {
  accounts, categories, isLoadingData, tipoOpcoes,
  tipo, valor, descricao, categoria, conta, data, error,
  validate, isValid, buildPayload, fillFrom,
} = useLancamentoForm()

const isLoading = ref(false)

watch(
  () => props.transaction,
  (transaction: Transaction | null) => {
    if (transaction) fillFrom(transaction)
  },
  { immediate: true },
)

async function submit() {
  if (!props.transaction) return
  error.value = validate()
  if (error.value) return

  isLoading.value = true
  try {
    await updateTransaction(props.transaction.id, buildPayload())
    emit('close')
  } catch {
    addToast('Erro ao salvar. Tente novamente.', 'alert')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* ── Type toggle ─────────────────────────────────────────── */
.tipo-toggle {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 4px;
  margin-bottom: 20px;
}

.tipo-btn {
  height: 34px;
  border-radius: var(--r);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--bd2);
  background: var(--sf);
  color: var(--t3);
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.tipo-btn.active {
  background: var(--blue);
  color: #0E1112;
  border-color: var(--blue);
}

/* ── Valor hero input ────────────────────────────────────── */
.valor-wrap {
  display: flex;
  align-items: center;
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  transition: border-color 0.12s;
}

.valor-wrap:focus-within {
  border-color: var(--blue);
}

.valor-prefix {
  font-size: 16px;
  color: var(--t3);
  font-family: 'Space Grotesk', monospace;
  margin-right: 8px;
  flex-shrink: 0;
}

.valor-input {
  font-family: 'Space Grotesk', monospace;
  font-size: 32px;
  font-weight: 300;
  color: var(--t1);
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
}

.valor-input.receita {
  color: var(--ok);
}

.valor-input::placeholder {
  color: var(--t3);
}

/* ── Form labels (sentence case) ─────────────────────────── */
.flbl {
  font-size: 12px;
  font-weight: 500;
  color: var(--t3);
  margin-bottom: 6px;
}

/* ── Shared field style ──────────────────────────────────── */
.field {
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: var(--r);
  padding: 10px 12px;
  min-height: 40px;
  color: var(--t1);
  font-size: 14px;
  width: 100%;
  outline: none;
  font-family: inherit;
  transition: border-color 0.12s;
  display: block;
  box-sizing: border-box;
}

.field:focus {
  border-color: var(--blue);
}

.field::placeholder {
  color: var(--t3);
}

/* ── Select ─────────────────────────────────────────────── */
.select-wrap {
  position: relative;
}

.select {
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
  padding-right: 28px;
}

.select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--t3);
  font-size: 12px;
  pointer-events: none;
  line-height: 1;
}

/* ── Two-column row ─────────────────────────────────────── */
.row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

/* ── Date input ─────────────────────────────────────────── */
input[type="date"] {
  color-scheme: dark;
}

/* ── CTA ────────────────────────────────────────────────── */
.cta {
  height: 40px;
  width: 100%;
  font-size: 13px;
  font-weight: 600;
}
</style>
