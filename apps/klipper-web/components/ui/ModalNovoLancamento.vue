<template>
  <UiBaseModal title="Novo lançamento" :open="open" @close="requestClose">

    <div v-if="confirmDiscard" role="alert" class="discard-confirm">
      <p>Descartar este lançamento?</p>
      <div class="discard-actions">
        <button ref="keepButton" class="btn btn-ghost" type="button" data-testid="manter-rascunho" @click="keepDraft">Continuar editando</button>
        <button class="btn btn-p" type="button" data-testid="descartar-rascunho" @click="discard">Descartar</button>
      </div>
    </div>

    <div v-else>
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
        ref="amountInput"
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

    <div style="margin-bottom:16px">
      <p class="flbl">Situação</p>
      <div class="select-wrap">
        <select v-model="status" class="field select" aria-label="Situação do lançamento">
          <option value="efetivado">Efetivado</option>
          <option value="previsto">Previsto — não altera o saldo</option>
          <option value="conciliado">Conciliado</option>
        </select>
        <span class="select-arrow">▾</span>
      </div>
    </div>

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

      <div v-if="tipo === 'transferencia'">
        <p class="flbl">Conta de destino</p>
        <div class="select-wrap">
          <select v-model="contaDestino" class="field select" aria-label="Conta de destino">
            <option :value="null">Selecionar destino</option>
            <option v-for="acc in accounts.filter((acc) => acc.id !== conta)" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
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

    <div v-if="!isLoadingData" style="margin-bottom:16px">
      <p class="flbl">Portador (opcional)</p>
      <div class="select-wrap">
        <select v-model="portador" class="field select" aria-label="Portador do lançamento">
          <option :value="null">Sem portador</option>
          <option v-for="member in members" :key="member.id" :value="member.id">{{ member.name }}</option>
        </select>
        <span class="select-arrow">▾</span>
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
      role="alert"
      style="font-size:12px;color:var(--alert);margin-bottom:10px;padding:8px 12px;background:var(--ald);border-radius:var(--r)"
    >
      {{ error }}
    </div>

    <!-- CTA -->
    <button
      class="btn btn-p cta"
      type="button"
      :disabled="isLoading || !isValid"
      @click="submit"
    >
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>{{ ctaLabel }}</span>
    </button>
    </div>

  </UiBaseModal>
</template>

<script setup lang="ts">
const { open } = defineProps<{ open: boolean }>()
const emit = defineEmits(['close'])

const { createTransaction } = useTransactions()
const { createTransfer } = useTransfers()
const {
  accounts, categories, members, isLoadingData, tipoOpcoes,
  tipo, valor, descricao, categoria, conta, contaDestino, portador, status, data, error,
  validate, isValid, buildPayload,
} = useLancamentoForm()

const isLoading = ref(false)
const confirmDiscard = ref(false)
const keepButton = ref<HTMLButtonElement | null>(null)
const amountInput = ref<HTMLInputElement | null>(null)

function keepDraft() {
  confirmDiscard.value = false
  nextTick(() => amountInput.value?.focus())
}

function resetForm() {
  tipo.value = 'gasto'
  valor.value = ''
  descricao.value = ''
  conta.value = null
  contaDestino.value = null
  categoria.value = null
  portador.value = null
  status.value = 'efetivado'
  data.value = todayISO()
  error.value = null
}

function requestClose() {
  if (isLoading.value) return
  if (confirmDiscard.value) {
    keepDraft()
    return
  }
  const dirty = valor.value || descricao.value || conta.value || contaDestino.value || categoria.value ||
    portador.value || tipo.value !== 'gasto' || status.value !== 'efetivado' || data.value !== todayISO()
  if (dirty) {
    confirmDiscard.value = true
    nextTick(() => keepButton.value?.focus())
  }
  else emit('close')
}

function discard() {
  resetForm()
  confirmDiscard.value = false
  emit('close')
}

const ctaLabel = computed(() => {
  if (tipo.value === 'receita') return 'Registrar receita'
  if (tipo.value === 'transferencia') return 'Registrar transferência'
  return 'Registrar gasto'
})

async function submit() {
  error.value = validate()
  if (error.value) return

  isLoading.value = true
  try {
    const payload = buildPayload()
    if (tipo.value === 'transferencia') {
      await createTransfer({
        source_account_id: conta.value!,
        destination_account_id: contaDestino.value!,
        amount: payload.amount!, occurred_on: payload.occurred_on!, description: payload.description!,
      })
    } else {
      await createTransaction(payload)
    }
    emit('close')
    resetForm()
  } catch {
    error.value = 'Não foi possível salvar. Seus dados continuam aqui. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.discard-confirm {
  padding: 12px;
  margin-bottom: 16px;
  border: 1px solid var(--bd2);
  border-radius: var(--r);
  color: var(--t1);
}

.discard-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

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
