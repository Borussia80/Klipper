<template>
  <div ref="mountEl" class="sparkline-host" />
</template>

<script setup lang="ts">
/**
 * PatrimonioSparkline — React island via manual mount.
 * Renders a minimal area sparkline using Recharts.
 * This is client-only (chart reads DOM dimensions).
 */

const props = defineProps<{ data: number[] }>()
const mountEl = ref<HTMLDivElement | null>(null)

// React mount is client-only
onMounted(async () => {
  if (!mountEl.value) return

  const React = (await import('react')).default
  const { createRoot } = await import('react-dom/client')
  const {
    AreaChart, Area, ResponsiveContainer, Tooltip,
  } = await import('recharts')

  const chartData = props.data.map((v, i) => ({ i, v }))

  const SparkTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null
    return React.createElement(
      'div',
      { style: { fontFamily: "'Geist Mono', monospace", fontSize: '0.65rem', color: '#8BA3BE', padding: '4px 8px', background: '#151D2A', border: '1px solid #1E2D3F', borderRadius: 4 } },
      new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact', maximumFractionDigits: 0 }).format(payload[0].value),
    )
  }

  const el = React.createElement(
    ResponsiveContainer,
    { width: '100%', height: 60 },
    React.createElement(
      AreaChart,
      { data: chartData, margin: { top: 2, right: 0, left: 0, bottom: 0 } },
      React.createElement('defs', null,
        React.createElement('linearGradient', { id: 'sparkGrad', x1: '0', y1: '0', x2: '0', y2: '1' },
          React.createElement('stop', { offset: '5%', stopColor: '#4F7BFF', stopOpacity: 0.3 }),
          React.createElement('stop', { offset: '95%', stopColor: '#4F7BFF', stopOpacity: 0 }),
        ),
      ),
      React.createElement(Tooltip, { content: React.createElement(SparkTooltip) }),
      React.createElement(Area, {
        type: 'monotone',
        dataKey: 'v',
        stroke: '#4F7BFF',
        strokeWidth: 1.5,
        fill: 'url(#sparkGrad)',
        dot: false,
        activeDot: { r: 3, fill: '#4F7BFF', strokeWidth: 0 },
        isAnimationActive: true,
        animationDuration: 600,
        animationEasing: 'ease-out',
      }),
    ),
  )

  const root = createRoot(mountEl.value)
  root.mount(el)

  onUnmounted(() => root.unmount())
})
</script>

<style scoped>
.sparkline-host {
  width: 100%;
  height: 60px;
}
</style>
