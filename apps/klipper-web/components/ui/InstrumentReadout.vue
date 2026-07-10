<script setup lang="ts">
/**
 * Instrumento primário da tela (padrão HMI, ISA-101).
 * Um por página: o número que responde a pergunta da tela, com barra de
 * faixa estilo bargraph. Único elemento da tela autorizado a usar --ok.
 */
const props = defineProps<{
  label: string
  value: string
  ratio: number
  detail?: string
}>()

const pct = computed(() => Math.round(Math.min(1, Math.max(0, props.ratio)) * 100))
</script>

<template>
  <div>
    <div class="plbl" style="margin-bottom:10px">{{ label }}</div>
    <div class="mono readout-value">{{ value }}</div>

    <div class="readout-track" role="presentation">
      <div
        data-testid="readout-bar"
        class="readout-fill"
        :style="{ width: pct + '%' }"
      ></div>
    </div>

    <div v-if="detail" data-testid="readout-detail" class="readout-detail">
      {{ detail }}
    </div>
  </div>
</template>

<style scoped>
.readout-value {
  font-size: clamp(44px, 8vw, 72px);
  font-weight: 300;
  letter-spacing: -0.03em;
  line-height: 0.95;
  color: var(--ok);
}

.readout-track {
  margin-top: 20px;
  height: 3px;
  background: var(--ly);
  border-radius: 2px;
  position: relative;
}

/* ticks de faixa (min / meio / max), discretos como num bargraph */
.readout-track::before,
.readout-track::after {
  content: '';
  position: absolute;
  top: -3px;
  width: 1px;
  height: 9px;
  background: var(--bd2);
}
.readout-track::before { left: 50%; }
.readout-track::after  { right: 0; }

.readout-fill {
  height: 100%;
  background: var(--ok);
  border-radius: 2px;
  opacity: 0.7;
}

.readout-detail {
  margin-top: 10px;
  font-size: 12px;
  color: var(--t3);
}
</style>
