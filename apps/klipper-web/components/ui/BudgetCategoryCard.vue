<template>
  <div
    class="bc"
    :class="{
      'bc-w': status === 'warn',
      'bc-a': status === 'alert',
    }"
  >
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="display:flex;align-items:center;gap:10px">
        <UiAppIcon :name="icon" :size="20" style="flex-shrink:0;color:var(--t2)" />
        <div>
          <div style="font-size:14px;font-weight:600;color:var(--t1)">{{ name }}</div>
          <div
            :style="{ fontSize: '11px', color: status === 'alert' ? 'var(--alert)' : 'var(--t3)' }"
          >
            <template v-if="status === 'alert'">
              Limite excedido em R$ {{ overshoot.toFixed(0).replace('.', ',') }}
            </template>
            <template v-else>{{ daysLeft }} dias restantes</template>
          </div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <span
          v-if="status === 'alert'"
          class="tag tag-a"
        >ESTOURADO</span>
        <span
          v-else-if="status === 'warn'"
          class="tag tag-w"
        >{{ pct }}%</span>
        <span
          v-else
          class="tag tag-b"
        >{{ pct }}%</span>
        <button
          v-if="canEditReimbursement"
          type="button"
          style="display:flex;align-items:center;justify-content:center;background:none;border:none;padding:2px;cursor:pointer;color:var(--t4)"
          title="Editar vínculo de reembolso"
          aria-label="Editar vínculo de reembolso"
          @click="openEditReimbursement"
        >
          <UiAppIcon name="settings" :size="14" />
        </button>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:-4px 0 10px">
      <span style="font-size:11px;color:var(--t4)">{{ naturezaLabel }}</span>
      <span class="tag" :class="recorrenciaTagClass">{{ recorrenciaLabel }}</span>
      <span style="font-size:11px;color:var(--t4)">presente em {{ monthsPresent }} dos últimos {{ monthsTotal }} meses</span>
    </div>

    <div
      :style="{
        height: '10px',
        background: status === 'alert' ? 'var(--ald)' : 'var(--ly)',
        borderRadius: '5px',
        overflow: 'hidden',
        marginBottom: '8px',
      }"
    >
      <div
        :style="{
          width: `${Math.min(pct, 100)}%`,
          height: '100%',
          background: barColor,
          borderRadius: '5px',
        }"
      />
    </div>

    <div style="display:flex;justify-content:space-between;font-size:12px">
      <span :style="{ color: status === 'alert' ? 'var(--alert)' : 'var(--t2)' }">
        R$ {{ spent.toLocaleString('pt-BR', { minimumFractionDigits: 0 }) }} gastos
      </span>
      <span :style="{ color: status === 'alert' ? 'var(--alert)' : 'var(--t3)' }">
        <template v-if="status === 'alert'">
          R$ {{ overshoot.toFixed(0) }} acima do limite de R$ {{ limit.toLocaleString('pt-BR') }}
        </template>
        <template v-else>
          R$ {{ (limit - spent).toLocaleString('pt-BR', { minimumFractionDigits: 0 }) }} livres de R$ {{ limit.toLocaleString('pt-BR') }}
        </template>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  icon: string
  name: string
  pct: number
  spent: number
  limit: number
  daysLeft: number
  natureza: 'fixo' | 'cartao_parcelamento' | 'variavel'
  recorrencia: 'rotineiro' | 'ocasional' | 'pontual'
  monthsPresent: number
  monthsTotal: number
  categoryId?: number
}>()

const { categories } = useCategories()
const { open } = useModal()

const linkedCategory = computed(() => categories.value.find((c) => c.id === props.categoryId) ?? null)
const canEditReimbursement = computed(() => linkedCategory.value?.category_type === 'expense')

function openEditReimbursement() {
  if (linkedCategory.value) open('editar-categoria', linkedCategory.value)
}

const status = computed<'ok' | 'warn' | 'alert'>(() => {
  if (props.pct > 100) return 'alert'
  if (props.pct >= 80) return 'warn'
  return 'ok'
})

const NATUREZA_LABELS: Record<string, string> = {
  fixo: 'Fixo',
  cartao_parcelamento: 'Cartão/Parcelamento',
  variavel: 'Variável',
}

const RECORRENCIA_LABELS: Record<string, string> = {
  rotineiro: 'Rotineiro',
  ocasional: 'Ocasional',
  pontual: 'Pontual',
}

const RECORRENCIA_TAG_CLASS: Record<string, string> = {
  rotineiro: 'tag-b',
  ocasional: 'tag-i',
  pontual: 'tag-w',
}

const naturezaLabel = computed(() => NATUREZA_LABELS[props.natureza] ?? props.natureza)
const recorrenciaLabel = computed(() => RECORRENCIA_LABELS[props.recorrencia] ?? props.recorrencia)
const recorrenciaTagClass = computed(() => RECORRENCIA_TAG_CLASS[props.recorrencia] ?? 'tag-i')

const overshoot = computed(() => Math.max(0, props.spent - props.limit))

const barColor = computed(() => {
  if (status.value === 'alert') return 'var(--alert)'
  if (status.value === 'warn') return 'var(--warn)'
  return 'var(--blue)'
})
</script>
