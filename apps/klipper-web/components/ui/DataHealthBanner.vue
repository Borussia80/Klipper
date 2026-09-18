<template>
  <div v-if="visivel" class="dh" data-testid="data-health">
    <div class="dh-txt">
      <strong>{{ health!.uncategorized }} de {{ health!.transactions }}</strong> lançamentos ainda estão
      sem categoria. O orçamento e os relatórios por categoria ficam vazios até isso ser feito.
    </div>

    <div class="dh-track">
      <span class="dh-fill" data-testid="data-health-bar" :style="{ width: `${pct}%` }" />
    </div>

    <NuxtLink class="btn btn-p dh-cta" to="/transacoes">Categorizar lançamentos</NuxtLink>
  </div>
</template>

<script setup lang="ts">
/**
 * A faixa que explica por que o resto da tela está vazio.
 *
 * O extrato importado entra sem categoria, e tudo que depende de categoria —
 * orçamento, relatórios, composição de gastos — fica vazio por consequência.
 * Sem o número na tela, o usuário atribui isso ao app.
 */
import type { DataHealthReport } from '~/composables/useReports'

const props = defineProps<{ health: DataHealthReport | null }>()

// Metade: abaixo disso a categorização não é o que está travando as telas, e a
// faixa viraria um alerta permanente sobre a sobra que sempre existe.
const LIMITE = 0.5

const pct = computed(() => {
  if (!props.health?.transactions) return 0
  return Math.round((props.health.uncategorized / props.health.transactions) * 100)
})

const visivel = computed(() => {
  const h = props.health
  if (!h || h.transactions === 0 || h.uncategorized === 0) return false
  return h.uncategorized / h.transactions >= LIMITE
})
</script>

<style scoped>
.dh {
  background: var(--wnd); border: 1px solid var(--warn); border-radius: var(--r);
  padding: 14px 16px; display: grid; gap: 10px;
}
.dh-txt { font-size: 13px; color: var(--t2); line-height: 1.5; }
.dh-txt strong { color: var(--warn); font-weight: 600; }

.dh-track { height: 5px; background: var(--sf); border-radius: 3px; overflow: hidden; }
.dh-fill { display: block; height: 100%; background: var(--warn); }

.dh-cta { justify-self: start; height: 34px; font-size: 12px; }
</style>
