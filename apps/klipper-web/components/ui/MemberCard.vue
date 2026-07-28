<script setup lang="ts">
/**
 * Reembolso não entra aqui de propósito: no modelo de dados do Klipper é
 * categoria de gasto na conta (pessoa/motivo são informação complementar da
 * categoria), não um vínculo estrutural a Member.
 */
const props = defineProps<{
  name: string
  relationship: 'titular' | 'dependente'
  spentLabel: string
}>()

const relationshipLabel = computed(() => (props.relationship === 'titular' ? 'Titular' : 'Dependente'))

const initials = computed(() =>
  props.name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join(''),
)
</script>

<template>
  <div class="ac">
    <div class="mem-avatar">{{ initials }}</div>
    <div style="flex:1;min-width:0">
      <div style="font-size:13px;font-weight:600;color:var(--t1)">{{ name }}</div>
      <div style="font-size:11px;color:var(--t3)">{{ relationshipLabel }}</div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div class="mono" style="font-size:13px;font-weight:500;color:var(--t1)">{{ spentLabel }}</div>
    </div>
  </div>
</template>

<style scoped>
.mem-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bd);
  color: var(--t1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
</style>
