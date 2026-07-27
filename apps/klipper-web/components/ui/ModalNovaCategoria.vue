<template>
  <UiBaseModal
    title="Nova categoria"
    subtitle="Crie um envelope de orçamento"
    :open="open"
    @close="$emit('close')"
  >
    <!-- Icon picker -->
    <div>
      <label class="flbl">Ícone</label>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px">
        <button
          v-for="opt in CATEGORY_ICONS"
          :key="opt.name"
          type="button"
          :title="opt.label"
          :aria-label="opt.label"
          :aria-pressed="selectedIcon === opt.name"
          class="icon-opt"
          :class="{ active: selectedIcon === opt.name }"
          @click="selectedIcon = opt.name"
        >
          <UiAppIcon :name="opt.name" :size="16" />
        </button>
      </div>
    </div>

    <!-- Natureza picker -->
    <div>
      <label class="flbl">Natureza</label>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px">
        <button
          v-for="opt in NATUREZA_OPTIONS"
          :key="opt.value"
          type="button"
          :aria-pressed="selectedNatureza === opt.value"
          class="nat-opt"
          :class="{ active: selectedNatureza === opt.value }"
          @click="selectedNatureza = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Reembolsada por (só para categorias de despesa) -->
    <div v-if="categoryType === 'expense'">
      <label class="flbl">Reembolsada por</label>
      <div class="sel-wrap">
        <select v-model="reimbursedByCategoryId" class="fi fi-sel" aria-label="Categoria de receita que reembolsa esta despesa">
          <option :value="null">Nenhuma</option>
          <option v-for="inc in incomes" :key="inc.id" :value="inc.id">{{ inc.name }}</option>
        </select>
        <span class="sel-caret">▾</span>
      </div>
    </div>

    <div>
      <label class="flbl">Nome</label>
      <input
        v-model="nome"
        type="text"
        placeholder="Ex: Restaurantes, Pets, Viagens…"
        class="fi"
        aria-label="Nome da categoria"
      />
    </div>

    <div style="margin-bottom:24px">
      <label class="flbl">Limite mensal</label>
      <div class="val-wrap">
        <span class="val-prefix">R$</span>
        <input
          v-model="limite"
          type="text"
          placeholder="0,00"
          class="fi fi-val"
          aria-label="Limite mensal em reais"
        />
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
      <span v-else>Criar categoria</span>
    </button>
  </UiBaseModal>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>()
const emit = defineEmits(['close'])

const { addToast } = useToast()
const { incomes, fetchCategories, createCategory } = useCategories()

onMounted(() => fetchCategories())

const CATEGORY_ICONS = [
  { name: 'shopping',   label: 'Mercado' },
  { name: 'home',       label: 'Moradia' },
  { name: 'car',        label: 'Transporte' },
  { name: 'health',     label: 'Saúde' },
  { name: 'gaming',     label: 'Lazer' },
  { name: 'restaurant', label: 'Restaurantes' },
  { name: 'clothing',   label: 'Vestuário' },
  { name: 'utilities',  label: 'Utilidades' },
  { name: 'education',  label: 'Educação' },
  { name: 'income',     label: 'Renda' },
  { name: 'investment', label: 'Investimento' },
  { name: 'transfer',   label: 'Transferência' },
  { name: 'music',      label: 'Música' },
  { name: 'travel',     label: 'Viagens' },
  { name: 'pet',        label: 'Pets' },
  { name: 'wallet',     label: 'Carteira' },
]

const ICON_TO_CATEGORY_TYPE: Record<string, string> = {
  income: 'income',
  transfer: 'transfer',
}

const NATUREZA_OPTIONS: { value: 'fixo' | 'cartao_parcelamento' | 'variavel'; label: string }[] = [
  { value: 'fixo', label: 'Fixo' },
  { value: 'cartao_parcelamento', label: 'Cartão/Parcelamento' },
  { value: 'variavel', label: 'Variável' },
]

const selectedIcon = ref('shopping')
const selectedNatureza = ref<'fixo' | 'cartao_parcelamento' | 'variavel'>('variavel')
const nome = ref('')
const limite = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const reimbursedByCategoryId = ref<number | null>(null)

const categoryType = computed(() => ICON_TO_CATEGORY_TYPE[selectedIcon.value] ?? 'expense')

function validate(): string | null {
  if (!nome.value.trim()) return 'Informe o nome da categoria'
  const l = parseFloat(limite.value.replace(',', '.'))
  if (!limite.value || isNaN(l) || l <= 0) return 'Informe um limite mensal válido'
  return null
}

async function submit() {
  error.value = validate()
  if (error.value) return
  isLoading.value = true
  try {
    await createCategory({
      name: nome.value.trim(),
      icon: selectedIcon.value || 'wallet',
      category_type: categoryType.value,
      color: '#6B93AE',
      natureza: selectedNatureza.value,
      reimbursed_by_category_id: categoryType.value === 'expense' ? reimbursedByCategoryId.value : null,
    })
    nome.value = ''
    limite.value = ''
    selectedIcon.value = 'shopping'
    selectedNatureza.value = 'variavel'
    reimbursedByCategoryId.value = null
    emit('close')
  } catch {
    addToast('Erro ao salvar. Tente novamente.', 'alert')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fi + .fi,
.fi ~ * {
  margin-top: 16px;
}
/* Nome field spacing */
div > .fi {
  margin-bottom: 16px;
}

/* Valor com prefixo */
.val-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.val-prefix {
  position: absolute;
  left: 12px;
  font-size: 13px;
  color: var(--t3);
  pointer-events: none;
  font-family: 'Space Grotesk', monospace;
  z-index: 1;
}
.fi-val {
  padding-left: 32px;
}

.icon-opt {
  width: 34px; height: 34px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 1px solid var(--bd2); background: var(--sf);
  color: var(--t3); transition: border-color .12s, color .12s, background .12s;
}
.icon-opt:hover { color: var(--t2); background: var(--ly); }
.icon-opt.active { border-color: var(--blue); background: var(--bdm); color: var(--blt); }
.icon-opt:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }

.nat-opt {
  height: 30px; padding: 0 12px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 1px solid var(--bd2); background: var(--sf);
  color: var(--t3); font-size: 12px; transition: border-color .12s, color .12s, background .12s;
}
.nat-opt:hover { color: var(--t2); background: var(--ly); }
.nat-opt.active { border-color: var(--blue); background: var(--bdm); color: var(--blt); }
.nat-opt:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
</style>
