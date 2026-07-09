<template>
  <div
    class="bc"
    :class="{ 'bc-a': rank === 0 }"
  >
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="display:flex;align-items:center;gap:10px">
        <UiAppIcon name="card" :size="20" style="flex-shrink:0;color:var(--t2)" />
        <div>
          <div style="font-size:14px;font-weight:600;color:var(--t1)">{{ row.name }}</div>
          <div v-if="row.institution" style="font-size:11px;color:var(--t3)">{{ row.institution }}</div>
        </div>
      </div>
      <span class="tag" :class="rank === 0 ? 'tag-a' : 'tag-i'">#{{ rank + 1 }}</span>
    </div>

    <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
      <div style="font-size:11px;color:var(--t3)">saldo da fatura</div>
      <div class="mono" style="font-size:14px;font-weight:500;color:var(--t1)">{{ formatBRL(row.saldo_fatura_atual) }}</div>
    </div>

    <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
      <div style="font-size:11px;color:var(--t3)">custo do rotativo neste ciclo</div>
      <div class="mono" style="font-size:14px;font-weight:600;color:var(--alert)">{{ formatBRL(row.encargos) }}</div>
    </div>

    <div style="font-size:11px;color:var(--t3);margin-bottom:10px">
      {{ formatPercentRaw(row.juros_rotativo_am) }} a.m.
      <template v-if="row.juros_rotativo_aa !== null"> · {{ formatPercentRaw(row.juros_rotativo_aa) }} a.a.</template>
    </div>

    <div style="font-size:12px;color:var(--t3);padding-top:10px;border-top:1px solid var(--bd)">
      pagando só o mínimo, o saldo sobe para
      <strong style="color:var(--t1)">{{ formatBRL(row.saldo_projetado_proximo_mes) }}</strong>
      {{ estimateLabel }}
    </div>

    <div
      v-if="row.saldo_atualizado_em"
      class="mono"
      :style="{ fontSize: '10px', marginTop: '8px', color: isStale ? 'var(--warn)' : 'var(--t4)' }"
    >
      {{ formatDaysAgo(row.saldo_atualizado_em) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DebtRankingRow } from '~/composables/useReports'

const props = defineProps<{
  rank: number
  row: DebtRankingRow
}>()

const { formatBRL, formatPercentRaw, formatDaysAgo } = useFormatters()

const estimateLabel = computed(() => {
  const missingIof = props.row.iof_projetado === null
  const missingMinimo = props.row.pagamento_minimo === null
  if (missingIof && missingMinimo) return '(estimativa sem IOF nem pagamento mínimo capturados)'
  if (missingIof) return '(estimativa sem IOF)'
  if (missingMinimo) return '(estimativa sem pagamento mínimo capturado)'
  return '(estimativa)'
})

const isStale = computed(() => {
  if (!props.row.saldo_atualizado_em) return false
  const days = (Date.now() - new Date(props.row.saldo_atualizado_em).getTime()) / 86_400_000
  return days > 30
})
</script>
