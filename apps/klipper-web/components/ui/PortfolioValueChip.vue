<script setup lang="ts">
/**
 * Header de investimentos.vue: total real do portfólio.
 * Não há current_price/histórico de cotação no backend, então a variação
 * nunca é inventada — mostra um chip neutro em vez de um percentual falso.
 */
defineProps<{ totalCost: number }>()
const { formatBRL } = useFormatters()
</script>

<template>
  <div class="pvc">
    <div class="pvc-val mono">{{ formatBRL(totalCost) }}</div>
    <div class="pvc-chip">Variação indisponível — histórico insuficiente</div>
  </div>
</template>

<style scoped>
.pvc { text-align: right; }
.pvc-val { font-size: 16px; font-weight: 500; color: var(--t1); line-height: 1.2; }
.pvc-chip { font-size: 11px; color: var(--t3); margin-top: 2px; }
</style>
