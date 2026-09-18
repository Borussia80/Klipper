<script setup lang="ts">
/**
 * Régua de ritmo do mês exibido, logo abaixo do hero: 80% da renda gasta no
 * dia 10 é outra história que no dia 28, e a barra de gasto sozinha não conta
 * essa diferença. Mês fechado não tem ritmo a medir — diz que encerrou em vez
 * de fingir uma porcentagem decorrida.
 */
const props = defineProps<{ year: number; month: number }>()

const hoje = new Date()

// Dia 0 do mês seguinte é o último dia deste mês — fevereiro bissexto incluso.
const diasNoMes = computed(() => new Date(props.year, props.month, 0).getDate())
const mesCorrente = computed(
  () => props.year === hoje.getFullYear() && props.month === hoje.getMonth() + 1
)
const diaAtual = computed(() => (mesCorrente.value ? hoje.getDate() : diasNoMes.value))
const pct = computed(() => Math.round((diaAtual.value / diasNoMes.value) * 100))
</script>

<template>
  <div class="ritmo">
    <div class="ritmo-bar" role="presentation">
      <div
        data-testid="ritmo-fill"
        class="fill"
        :class="{ fechado: !mesCorrente }"
        :style="{ width: pct + '%' }"
      ></div>
    </div>
    <div class="ritmo-scale">
      <span v-if="mesCorrente" data-testid="ritmo-dia">dia {{ diaAtual }} de {{ diasNoMes }}</span>
      <span v-else data-testid="ritmo-fechado">mês encerrado</span>
      <span v-if="mesCorrente" data-testid="ritmo-pct" class="mono">{{ pct }}% do mês decorrido</span>
      <span v-else class="mono">{{ diasNoMes }} dias</span>
    </div>
  </div>
</template>

<style scoped>
.ritmo-bar {
  height: 4px; border-radius: 3px;
  background: #0A121C; border: 1px solid var(--bd); overflow: hidden; display: flex;
}
.ritmo-bar .fill { height: 100%; background: var(--sea); }
.ritmo-bar .fill.fechado { background: var(--bd-hi); }
.ritmo-scale {
  display: flex; justify-content: space-between; margin-top: 6px;
  font-size: 11.5px; color: var(--t3);
}
</style>
