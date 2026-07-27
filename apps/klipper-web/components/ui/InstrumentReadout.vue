<script setup lang="ts">
/**
 * Hero faceplate do dashboard (direção náutica premium).
 * Instrumento primário: resultado do mês, com moldura, gradiente e barra
 * de faixa — nunca um número solto no vazio.
 */
const props = defineProps<{
  label: string
  netValue: number
  formattedValue: string
  spentRatio: number
  detail?: string
}>()

const pct = computed(() => Math.round(Math.min(1, Math.max(0, props.spentRatio)) * 100))
const isOver = computed(() => props.spentRatio > 1)
const scaleLabel = computed(() =>
  isOver.value ? 'Saídas já superam entradas do ciclo' : 'Dentro da faixa do ciclo'
)
</script>

<template>
  <div class="hero">
    <div class="hero-lbl">{{ label }}</div>
    <div class="hero-row">
      <div class="hero-num mono" :class="netValue < 0 ? 'neg' : 'pos'">{{ formattedValue }}</div>
      <div v-if="detail" data-testid="readout-detail" class="hero-delta">{{ detail }}</div>
    </div>
    <div class="hero-bar" role="presentation">
      <div
        data-testid="readout-bar"
        class="fill"
        :class="{ over: isOver }"
        :style="{ width: pct + '%' }"
      ></div>
    </div>
    <div class="hero-scale">
      <span>{{ scaleLabel }}</span>
      <span class="mono">{{ Math.round(spentRatio * 100) }}% da renda</span>
    </div>
  </div>
</template>

<style scoped>
.hero {
  background: linear-gradient(160deg, #13202E, #0E1622);
  border: 1px solid var(--bd-hi);
  border-radius: var(--r);
  padding: 26px 28px;
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: '';
  position: absolute; top: -40%; right: -10%; width: 340px; height: 340px;
  background: radial-gradient(circle, rgba(217,168,92,0.10), transparent 62%);
  pointer-events: none;
}
.hero-lbl {
  font-size: 12px; color: var(--t3); text-transform: uppercase;
  letter-spacing: .09em; font-weight: 600;
}
.hero-row { display: flex; align-items: flex-end; gap: 20px; margin-top: 8px; flex-wrap: wrap; }
.hero-num { font-size: clamp(36px, 6vw, 52px); font-weight: 600; line-height: 1; }
.hero-num.pos { color: var(--ok); }
.hero-num.neg { color: var(--alert); }
.hero-delta { font-size: 13px; color: var(--t2); padding-bottom: 6px; }
.hero-bar {
  margin-top: 20px; height: 8px; border-radius: 5px;
  background: #0A121C; border: 1px solid var(--bd); overflow: hidden; display: flex;
}
.hero-bar .fill { height: 100%; background: linear-gradient(90deg, var(--brass), #C7954C); }
.hero-bar .fill.over { background: linear-gradient(90deg, var(--warn), var(--alert)); }
.hero-scale {
  display: flex; justify-content: space-between; margin-top: 7px;
  font-size: 11.5px; color: var(--t3);
}
</style>
