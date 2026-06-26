<template>
  <UiBaseModal title="Novo lançamento" :open="open" @close="$emit('close')">

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
    <p class="plbl">Valor</p>
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
    <p class="plbl">Descrição</p>
    <input
      v-model="descricao"
      class="field"
      type="text"
      placeholder="Ex: Supermercado Extra"
      style="margin-bottom:16px"
      aria-label="Descrição do lançamento"
    />

    <!-- Categoria + Conta -->
    <div class="row-two">
      <div>
        <p class="plbl">Categoria</p>
        <div class="select-wrap">
          <select v-model="categoria" class="field select" aria-label="Categoria do lançamento">
            <option value="alimentacao">Alimentação</option>
            <option value="moradia">Moradia</option>
            <option value="transporte">Transporte</option>
            <option value="saude">Saúde</option>
            <option value="lazer">Lazer</option>
            <option value="restaurantes">Restaurantes</option>
            <option value="vestuario">Vestuário</option>
            <option value="utilidades">Utilidades</option>
            <option value="educacao">Educação</option>
            <option value="renda">Renda</option>
            <option value="investimento">Investimento</option>
            <option value="transferencia">Transferência</option>
          </select>
          <span class="select-arrow">▾</span>
        </div>
      </div>

      <div>
        <p class="plbl">Conta</p>
        <div class="select-wrap">
          <select v-model="conta" class="field select" aria-label="Conta de origem">
            <option value="nubank-conta">Nubank Conta</option>
            <option value="nubank-credito">Nubank Crédito</option>
            <option value="itau">Itaú</option>
            <option value="btg">BTG Pactual</option>
          </select>
          <span class="select-arrow">▾</span>
        </div>
      </div>
    </div>

    <!-- Data -->
    <p class="plbl">Data</p>
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
      :disabled="isLoading"
      @click="submit"
    >
      <span v-if="isLoading" class="btn-spinner" />
      <span v-else>{{ ctaLabel }}</span>
    </button>

  </UiBaseModal>
</template>

<script setup lang="ts">
const props = defineProps<{ open: boolean }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()

const tipoOpcoes = [
  { value: 'gasto', label: 'Gasto' },
  { value: 'receita', label: 'Receita' },
  { value: 'transferencia', label: 'Transferência' },
] as const

const tipo = ref<'gasto' | 'receita' | 'transferencia'>('gasto')
const valor = ref('')
const descricao = ref('')
const categoria = ref('alimentacao')
const conta = ref('nubank-conta')
const data = ref(new Date().toISOString().split('T')[0])
const isLoading = ref(false)
const error = ref<string | null>(null)

const ctaLabel = computed(() => {
  if (tipo.value === 'receita') return 'Registrar receita'
  if (tipo.value === 'transferencia') return 'Registrar transferência'
  return 'Registrar gasto'
})

function validate(): string | null {
  const v = parseFloat(valor.value.replace(',', '.'))
  if (!valor.value || isNaN(v) || v <= 0) return 'Informe um valor válido'
  if (!descricao.value.trim()) return 'Informe uma descrição'
  return null
}

async function submit() {
  error.value = validate()
  if (error.value) return

  isLoading.value = true
  try {
    await new Promise((r) => setTimeout(r, 600))
    addToast(`${ctaLabel.value.replace('Registrar', 'Lançamento')} registrado`, 'ok')
    emit('close')
    valor.value = ''
    descricao.value = ''
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
  color: #fff;
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
  font-family: 'JetBrains Mono', monospace;
  margin-right: 8px;
  flex-shrink: 0;
}

.valor-input {
  font-family: 'JetBrains Mono', monospace;
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
  color: var(--t4);
}

/* ── Shared field style ──────────────────────────────────── */
.field {
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: var(--r);
  padding: 9px 12px;
  color: var(--t1);
  font-size: 13px;
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
  color: var(--t4);
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
