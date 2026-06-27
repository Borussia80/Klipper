<template>
  <div class="txr" :style="borderStyle">
    <div
      :style="{
        width: '36px',
        height: '36px',
        borderRadius: '9px',
        background: iconBg,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '18px',
        flexShrink: '0',
      }"
    >
      {{ icon }}
    </div>
    <div>
      <div style="font-size:13px;font-weight:500;color:var(--t1)">{{ label }}</div>
      <div style="font-size:11px;color:var(--t3);margin-top:1px;display:flex;align-items:center;gap:5px">
        {{ sublabel }}
        <span
          v-if="tag"
          :class="`tag tag-${tag.variant}`"
        >{{ tag.text }}</span>
      </div>
      <div v-if="account" style="font-size:10px;color:var(--t4);margin-top:1px">{{ account }}</div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div
        class="mono"
        style="font-size:13px;font-weight:500"
        :style="{ color: amountColor || 'var(--t2)' }"
      >
        {{ amount }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  icon: string
  label: string
  sublabel?: string
  account?: string
  amount: string
  amountColor?: string
  iconBg?: string
  borderAlert?: 'warn' | 'alert'
  tag?: { text: string; variant: 'warn' | 'alert' | 'ok' | 'info' }
}>()

const iconBg = computed(() => props.iconBg || 'rgba(138,171,202,0.1)')
const borderStyle = computed(() => {
  if (props.borderAlert === 'warn')
    return { borderLeft: '3px solid var(--warn)', paddingLeft: '11px', marginLeft: '-8px' }
  if (props.borderAlert === 'alert')
    return { borderLeft: '3px solid var(--alert)', paddingLeft: '11px', marginLeft: '-8px' }
  return {}
})
</script>
