<template>
  <div
    class="bc"
    :class="{ 'bc-a': alert }"
  >
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="display:flex;align-items:center;gap:10px">
        <UiAppIcon :name="icon ?? 'wallet'" :size="20" style="flex-shrink:0;color:var(--t2)" />
        <div>
          <div style="font-size:14px;font-weight:600;color:var(--t1)">{{ name }}</div>
          <div style="font-size:11px;color:var(--t3)">reembolsado por {{ reimbursedByName }}</div>
        </div>
      </div>
      <span
        v-if="alert"
        class="tag tag-a"
      >ALERTA</span>
      <span
        v-else
        class="tag tag-b"
      >{{ coveragePct !== null ? `${Math.round(coveragePct)}%` : '--' }}</span>
    </div>

    <div
      :style="{
        height: '10px',
        background: alert ? 'var(--ald)' : 'var(--ly)',
        borderRadius: '5px',
        overflow: 'hidden',
        marginBottom: '8px',
      }"
    >
      <div
        :style="{
          width: `${Math.min(coveragePct ?? 0, 100)}%`,
          height: '100%',
          background: alert ? 'var(--alert)' : 'var(--blue)',
          borderRadius: '5px',
        }"
      />
    </div>

    <div style="font-size:12px;color:var(--t3)">
      gasto R$ {{ spent.toLocaleString('pt-BR', { minimumFractionDigits: 0 }) }}
      · reembolsado R$ {{ reimbursed.toLocaleString('pt-BR', { minimumFractionDigits: 0 }) }}
      · média histórica {{ historicalAvgPct !== null ? `${Math.round(historicalAvgPct)}%` : '--' }} ({{ monthsConsidered }} {{ monthsConsidered === 1 ? 'mês' : 'meses' }})
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string | null
  name: string
  reimbursedByName: string
  spent: number
  reimbursed: number
  coveragePct: number | null
  historicalAvgPct: number | null
  monthsConsidered: number
  alert: boolean
}>()
</script>
