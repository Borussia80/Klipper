<template>
  <div ref="mountEl" class="timeline-host" />
</template>

<script setup lang="ts">
/**
 * PatrimonioTimeline — React island.
 * Full-width area chart of net worth over time with period switching.
 */

const props = defineProps<{ period: '3m' | '6m' | '1a' | 'max' }>()
const mountEl = ref<HTMLDivElement | null>(null)
let root: any = null

// Mock data per period
const MOCK_DATA: Record<string, { date: string; value: number }[]> = {
  '3m': [
    { date: 'Abr', value: 458000 },
    { date: 'Mai', value: 471000 },
    { date: 'Jun', value: 487320 },
  ],
  '6m': [
    { date: 'Jan', value: 420000 },
    { date: 'Fev', value: 435000 },
    { date: 'Mar', value: 441000 },
    { date: 'Abr', value: 452000 },
    { date: 'Mai', value: 471000 },
    { date: 'Jun', value: 487320 },
  ],
  '1a': [
    { date: 'Jul', value: 380000 },
    { date: 'Ago', value: 390000 },
    { date: 'Set', value: 395000 },
    { date: 'Out', value: 405000 },
    { date: 'Nov', value: 410000 },
    { date: 'Dez', value: 420000 },
    { date: 'Jan', value: 435000 },
    { date: 'Fev', value: 441000 },
    { date: 'Mar', value: 452000 },
    { date: 'Abr', value: 458000 },
    { date: 'Mai', value: 471000 },
    { date: 'Jun', value: 487320 },
  ],
  max: [
    { date: '2023', value: 250000 },
    { date: 'Fev', value: 270000 },
    { date: 'Mai', value: 295000 },
    { date: 'Ago', value: 310000 },
    { date: '2024', value: 340000 },
    { date: 'Mar', value: 365000 },
    { date: 'Jun', value: 380000 },
    { date: 'Set', value: 395000 },
    { date: 'Dez', value: 420000 },
    { date: '2025', value: 435000 },
    { date: 'Mar', value: 452000 },
    { date: 'Jun', value: 487320 },
  ],
}

const fmtBRL = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact', maximumFractionDigits: 0 })

async function mount() {
  if (!mountEl.value) return

  const React = (await import('react')).default
  const { createRoot } = await import('react-dom/client')
  const {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  } = await import('recharts')

  const data = MOCK_DATA[props.period]

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null
    return React.createElement(
      'div',
      {
        style: {
          fontFamily: "'Geist Mono', monospace",
          fontSize: '0.72rem',
          color: '#F1F5F9',
          padding: '8px 12px',
          background: '#151D2A',
          border: '1px solid #1E2D3F',
          borderRadius: 6,
          lineHeight: 1.5,
        },
      },
      React.createElement('div', { style: { color: '#8BA3BE', fontSize: '0.62rem', marginBottom: 2 } }, label),
      React.createElement('div', { style: { color: '#4F7BFF' } }, fmtBRL.format(payload[0].value)),
    )
  }

  const el = React.createElement(
    ResponsiveContainer,
    { width: '100%', height: 200 },
    React.createElement(
      AreaChart,
      { data, margin: { top: 8, right: 8, left: 0, bottom: 0 } },
      React.createElement('defs', null,
        React.createElement('linearGradient', { id: 'timelineGrad', x1: '0', y1: '0', x2: '0', y2: '1' },
          React.createElement('stop', { offset: '5%', stopColor: '#4F7BFF', stopOpacity: 0.18 }),
          React.createElement('stop', { offset: '95%', stopColor: '#4F7BFF', stopOpacity: 0 }),
        ),
      ),
      React.createElement(CartesianGrid, {
        strokeDasharray: '0',
        stroke: 'rgba(255,255,255,0.04)',
        vertical: false,
      }),
      React.createElement(XAxis, {
        dataKey: 'date',
        tick: { fontFamily: "'Geist Mono', monospace", fontSize: 10, fill: '#4E6B87' },
        axisLine: false,
        tickLine: false,
        dy: 8,
      }),
      React.createElement(YAxis, {
        tickFormatter: (v: number) => fmtBRL.format(v),
        tick: { fontFamily: "'Geist Mono', monospace", fontSize: 10, fill: '#4E6B87' },
        axisLine: false,
        tickLine: false,
        width: 72,
      }),
      React.createElement(Tooltip, { content: React.createElement(CustomTooltip) }),
      React.createElement(Area, {
        type: 'monotone',
        dataKey: 'value',
        stroke: '#4F7BFF',
        strokeWidth: 2,
        fill: 'url(#timelineGrad)',
        dot: false,
        activeDot: { r: 4, fill: '#4F7BFF', stroke: '#0C1220', strokeWidth: 2 },
        isAnimationActive: true,
        animationDuration: 500,
        animationEasing: 'ease-out',
      }),
    ),
  )

  if (!root) {
    root = createRoot(mountEl.value)
  }
  root.render(el)
}

onMounted(mount)
watch(() => props.period, mount)
onUnmounted(() => root?.unmount())
</script>

<style scoped>
.timeline-host {
  width: 100%;
  height: 200px;
}
</style>
