<template>
  <UiBaseModal
    title="Novo aporte"
    subtitle="Registre uma operação de investimento"
    :open="open"
    @close="$emit('close')"
  >
    <!-- Tipo toggle -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:20px">
      <button
        :style="tipoOp === 'compra'
          ? 'background:var(--blue);color:#fff;border:1px solid var(--blue);border-radius:var(--r);padding:8px 0;font-size:13px;font-weight:600;cursor:pointer'
          : 'background:var(--sf);color:var(--t3);border:1px solid var(--bd2);border-radius:var(--r);padding:8px 0;font-size:13px;font-weight:600;cursor:pointer'"
        type="button"
        :aria-pressed="tipoOp === 'compra'"
        @click="tipoOp = 'compra'"
      >
        Compra
      </button>
      <button
        :style="tipoOp === 'venda'
          ? 'background:var(--blue);color:#fff;border:1px solid var(--blue);border-radius:var(--r);padding:8px 0;font-size:13px;font-weight:600;cursor:pointer'
          : 'background:var(--sf);color:var(--t3);border:1px solid var(--bd2);border-radius:var(--r);padding:8px 0;font-size:13px;font-weight:600;cursor:pointer'"
        type="button"
        :aria-pressed="tipoOp === 'venda'"
        @click="tipoOp = 'venda'"
      >
        Venda
      </button>
    </div>

    <div>
      <label class="plbl">Ativo</label>
      <input
        v-model="ativo"
        type="text"
        placeholder="Ticker ou nome (ex: IVVB11)"
        class="fi"
        aria-label="Ticker ou nome do ativo"
      />
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div>
        <label class="plbl">Quantidade</label>
        <input
          v-model="quantidade"
          type="number"
          placeholder="0"
          class="fi"
          aria-label="Quantidade de cotas ou ações"
        />
      </div>
      <div>
        <label class="plbl">Preço unitário</label>
        <input
          v-model="preco"
          type="text"
          placeholder="R$ 0,00"
          class="fi"
          aria-label="Preço unitário em reais"
        />
      </div>
    </div>

    <div style="margin-bottom:24px">
      <label class="plbl">Data</label>
      <input
        v-model="data"
        type="date"
        class="fi"
        aria-label="Data da operação"
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
      <span v-else>{{ tipoOp === 'compra' ? 'Registrar compra' : 'Registrar venda' }}</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { createInvestment } = useInvestments()

const tipoOp = ref<'compra' | 'venda'>('compra')
const ativo = ref('')
const quantidade = ref('')
const preco = ref('')
const data = ref(new Date().toISOString().split('T')[0])
const isLoading = ref(false)
const error = ref<string | null>(null)

function validate(): string | null {
  if (!ativo.value.trim()) return 'Informe o ativo'
  const q = parseFloat(quantidade.value)
  if (!quantidade.value || isNaN(q) || q <= 0) return 'Informe uma quantidade válida'
  const p = parseFloat(preco.value.replace(',', '.'))
  if (!preco.value || isNaN(p) || p <= 0) return 'Informe um preço válido'
  if (isFutureDate(data.value)) return 'A data não pode ser futura'
  return null
}

async function submit() {
  error.value = validate()
  if (error.value) return
  isLoading.value = true
  try {
    await createInvestment({
      ticker: ativo.value.trim().toUpperCase(),
      name: ativo.value.trim().toUpperCase(),
      investment_type: 'stock',
      quantity: parseFloat(quantidade.value),
      average_price: parseFloat(preco.value.replace(',', '.')),
      currency: 'BRL',
    })
    ativo.value = ''
    quantidade.value = ''
    preco.value = ''
    data.value = new Date().toISOString().split('T')[0]
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
input[type="date"].fi::-webkit-calendar-picker-indicator {
  filter: invert(0.5) sepia(1) saturate(0) brightness(0.8);
  cursor: pointer;
}
</style>
