<template>
  <div v-show="hasData" ref="mountEl" class="timeline-host" />
  <div v-show="!hasData" class="timeline-empty" data-testid="timeline-empty">
    Ainda não há histórico suficiente para o gráfico. O patrimônio é registrado a cada
    visita a esta página — volte em alguns meses para ver a evolução aqui.
  </div>
</template>

<script setup lang="ts">
/**
 * PatrimonioTimeline — React island.
 * Full-width area chart of net worth over time. Dados vêm de snapshots mensais
 * reais (net_worth_snapshots), registrados daqui pra frente — sem histórico
 * retroativo fabricado.
 */

const props = defineProps<{ data: { date: string; value: number }[] }>()
const mountEl = ref<HTMLDivElement | null>(null)
const hasData = computed(() => props.data.length >= 2)
let root: any = null

const fmtBRL = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact', maximumFractionDigits: 0 })

async function mount() {
  if (!mountEl.value || props.data.length < 2) return

  const React = (await import('react')).default
  const { createRoot } = await import('react-dom/client')
  const {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  } = await import('recharts')

  const data = props.data

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
watch(() => props.data, mount, { deep: true })
onUnmounted(() => root?.unmount())
</script>

<style scoped>
.timeline-host {
  width: 100%;
  height: 200px;
}
.timeline-empty {
  display: flex; align-items: center; justify-content: center;
  height: 200px; padding: 0 24px; text-align: center;
  color: var(--t3); font-size: 13px; line-height: 1.5;
}
</style>
