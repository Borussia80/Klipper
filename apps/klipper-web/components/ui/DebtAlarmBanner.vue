<script setup lang="ts">
/**
 * Alarme acionável do dashboard — cartão com maior custo de rotativo.
 * Visibilidade decidida pelo pai (v-if), não aqui. Sem "vence em": esse
 * campo não existe no sistema, só encargos/saldo/juros do rotativo.
 */
import type { DebtRankingRow } from '~/composables/useReports'

defineProps<{ row: DebtRankingRow }>()

const { formatBRL, formatPercentRaw } = useFormatters()
</script>

<template>
  <div class="alarm">
    <div class="alarm-ic">
      <svg viewBox="0 0 24 24" fill="none" stroke="var(--alert)" stroke-width="2" width="18" height="18" aria-hidden="true">
        <path d="M12 9v4M12 17h.01M10.3 3.9L2 18a2 2 0 001.7 3h16.6a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z" />
      </svg>
    </div>
    <div class="alarm-txt">
      <b>Fatura {{ row.name }} no rotativo</b><br />
      <span>
        {{ formatBRL(row.saldo_fatura_atual) }} · custo de {{ formatBRL(row.encargos) }} neste ciclo<template
          v-if="row.juros_rotativo_aa !== null"
        > · {{ formatPercentRaw(row.juros_rotativo_aa) }} a.a.</template>
      </span>
    </div>
    <NuxtLink to="/contas" class="alarm-cta">Ver prioridade →</NuxtLink>
  </div>
</template>

<style scoped>
.alarm {
  display: flex; align-items: center; gap: 12px;
  background: rgba(232,115,90,0.07); border: 1px solid rgba(232,115,90,0.28);
  border-radius: var(--r); padding: 14px 16px;
}
.alarm-ic {
  width: 34px; height: 34px; border-radius: 9px;
  background: rgba(232,115,90,0.14); display: grid; place-items: center; flex: none;
}
.alarm-txt { flex: 1; }
.alarm-txt b { color: var(--t1); font-weight: 600; }
.alarm-txt span { color: var(--t2); font-size: 13px; }
.alarm-cta {
  background: var(--alert); color: #2A0F0A; border: none; border-radius: 8px;
  padding: 8px 14px; font-weight: 600; font-size: 13px; cursor: pointer;
  flex: none; text-decoration: none; white-space: nowrap;
}
</style>
