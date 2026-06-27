<template>
  <div ref="mountEl" class="donut-host" />
</template>

<script setup lang="ts">
/**
 * AlocacaoDonut — React island.
 * Recharts PieChart with a custom center label showing total.
 */

interface Slice {
  name: string
  value: number
  color: string
}

const props = defineProps<{ data: Slice[]; total: number }>()
const mountEl = ref<HTMLDivElement | null>(null)

const fmtBRL = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  maximumFractionDigits: 0,
})

onMounted(async () => {
  if (!mountEl.value) return

  const React = (await import('react')).default
  const { createRoot } = await import('react-dom/client')
  const { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } = await import('recharts')

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null
    const item = payload[0]
    return React.createElement(
      'div',
      {
        style: {
          fontFamily: "'Geist Mono', monospace",
          fontSize: '0.72rem',
          padding: '8px 12px',
          background: '#151D2A',
          border: '1px solid #1E2D3F',
          borderRadius: 6,
          lineHeight: 1.6,
          color: '#F1F5F9',
        },
      },
      React.createElement('div', { style: { color: item.payload.color, marginBottom: 2 } }, item.name),
      React.createElement('div', null, fmtBRL.format(item.value)),
      React.createElement('div', { style: { color: '#4E6B87' } },
        new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format(
          item.value / props.total,
        ),
      ),
    )
  }

  // Center label using a custom label component
  const CenterLabel = () => React.createElement(
    'text',
    { x: '50%', y: '50%', textAnchor: 'middle', dominantBaseline: 'middle' },
    React.createElement('tspan', {
      x: '50%', dy: '-8',
      style: { fontFamily: "'Geist Mono', monospace", fontSize: '10px', fill: '#4E6B87', letterSpacing: '0.1em' },
    }, 'TOTAL'),
    React.createElement('tspan', {
      x: '50%', dy: '20',
      style: { fontFamily: "'Geist Mono', monospace", fontSize: '14px', fill: '#F1F5F9', fontWeight: 500 },
    }, fmtBRL.format(props.total)),
  )

  const el = React.createElement(
    ResponsiveContainer,
    { width: '100%', height: 240 },
    React.createElement(
      PieChart,
      null,
      React.createElement(Tooltip, { content: React.createElement(CustomTooltip) }),
      React.createElement(
        Pie,
        {
          data: props.data,
          cx: '50%',
          cy: '50%',
          innerRadius: '55%',
          outerRadius: '80%',
          paddingAngle: 2,
          dataKey: 'value',
          labelLine: false,
          label: CenterLabel,
          isAnimationActive: true,
          animationDuration: 600,
          animationEasing: 'ease-out',
        },
        ...props.data.map((entry, index) =>
          React.createElement(Cell, { key: index, fill: entry.color }),
        ),
      ),
    ),
  )

  const root = createRoot(mountEl.value)
  root.mount(el)
  onUnmounted(() => root.unmount())
})
</script>

<style scoped>
.donut-host {
  width: 100%;
  height: 240px;
}
</style>
