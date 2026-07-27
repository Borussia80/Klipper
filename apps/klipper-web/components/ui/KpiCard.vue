<script setup lang="ts">
/**
 * Card presentational da grid de 3 KPIs do dashboard.
 * chipTone 'neutral' (padrão) renderiza o rodapé como texto simples;
 * ok/warn/alert renderizam um chip colorido — nunca decoração livre.
 */
withDefaults(
  defineProps<{
    label: string
    icon: string
    value: string
    chipText?: string
    chipTone?: 'ok' | 'warn' | 'alert' | 'neutral'
  }>(),
  { chipTone: 'neutral' }
)
</script>

<template>
  <div class="card">
    <div class="kpi-top">
      <span class="kpi-lbl">{{ label }}</span>
      <div class="kpi-ic">
        <UiAppIcon :name="icon" :size="16" />
      </div>
    </div>
    <div class="kpi-val mono">{{ value }}</div>
    <div v-if="chipText" class="kpi-foot">
      <span v-if="chipTone !== 'neutral'" class="chip" :class="chipTone">{{ chipText }}</span>
      <template v-else>{{ chipText }}</template>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--sf); border: 1px solid var(--bd); border-radius: var(--r);
  padding: 17px 18px; transition: border-color .14s;
}
.card:hover { border-color: var(--bd-hi); }
.kpi-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.kpi-lbl { font-size: 12px; color: var(--t2); font-weight: 500; }
.kpi-ic {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--bg); border: 1px solid var(--bd); display: grid; place-items: center;
  color: var(--t2);
}
.kpi-val { font-size: 27px; font-weight: 600; letter-spacing: -.01em; }
.kpi-foot { font-size: 12px; color: var(--t3); margin-top: 5px; display: flex; align-items: center; gap: 6px; }
.chip { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 20px; font-family: 'Space Grotesk'; }
.chip.ok { background: rgba(67,197,158,0.13); color: var(--ok); }
.chip.warn { background: rgba(230,180,76,0.14); color: var(--warn); }
.chip.alert { background: rgba(232,115,90,0.14); color: var(--alert); }
</style>
