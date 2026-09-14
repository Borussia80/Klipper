<template>
  <div v-show="hasData" ref="hostEl" class="timeline-host">
    <svg
      :viewBox="`0 0 ${width} ${HEIGHT}`"
      class="timeline-svg"
      role="img"
      :aria-label="ariaLabel"
      data-testid="timeline-svg"
      @mousemove="onMove"
      @mouseleave="hoverIdx = null"
    >
      <defs>
        <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%" class="grad-top" />
          <stop offset="95%" class="grad-bottom" />
        </linearGradient>
      </defs>

      <line
        v-for="t in yTicks"
        :key="`g${t.value}`"
        class="grid-line"
        :x1="PAD.left"
        :x2="width - PAD.right"
        :y1="t.y"
        :y2="t.y"
      />

      <text
        v-for="t in yTicks"
        :key="`y${t.value}`"
        class="axis-label y-label"
        :x="PAD.left - 10"
        :y="t.y"
        :data-value="t.value"
        data-testid="y-tick"
        text-anchor="end"
        dominant-baseline="middle"
      >{{ t.label }}</text>

      <path :d="areaPath" :fill="`url(#${gradId})`" data-testid="timeline-area" />
      <path :d="linePath" class="timeline-line" data-testid="timeline-line" />

      <text
        v-for="t in xTicks"
        :key="`x${t.label}-${t.x}`"
        class="axis-label"
        :x="t.x"
        :y="HEIGHT - 6"
        data-testid="x-tick"
        text-anchor="middle"
      >{{ t.label }}</text>

      <circle
        v-if="hovered"
        class="active-dot"
        :cx="hovered.x"
        :cy="hovered.y"
        r="4"
      />
    </svg>

    <div
      v-if="hovered"
      class="timeline-tooltip"
      data-testid="timeline-tooltip"
      :style="tooltipStyle"
    >
      <div class="tt-date">{{ hovered.date }}</div>
      <div class="tt-value">{{ fmtFull.format(hovered.value) }}</div>
    </div>
  </div>

  <div v-show="!hasData" class="timeline-empty" data-testid="timeline-empty">
    Ainda não há histórico suficiente para o gráfico. O patrimônio é registrado a cada
    visita a esta página — volte em alguns meses para ver a evolução aqui.
  </div>
</template>

<script setup lang="ts">
/**
 * PatrimonioTimeline — área da evolução do patrimônio, em SVG nativo.
 *
 * Dados vêm de snapshots mensais reais (net_worth_snapshots), registrados daqui
 * pra frente — sem histórico retroativo fabricado. Com menos de 2 pontos não há
 * evolução a mostrar, e o componente cai no estado vazio.
 *
 * Os segmentos são retos, não suavizados: cada ponto é uma medição mensal
 * discreta, e a curva suave da versão anterior sugeria uma continuidade entre
 * as medições que o dado não tem.
 */

const props = defineProps<{ data: { date: string; value: number }[] }>()

const HEIGHT = 200
const PAD = { top: 8, right: 8, bottom: 24, left: 72 }
const FALLBACK_WIDTH = 640
const MAX_X_LABELS = 7

const hostEl = ref<HTMLElement | null>(null)
const width = ref(FALLBACK_WIDTH)
const hoverIdx = ref<number | null>(null)
const gradId = `tl-grad-${useId()}`

const fmtCompact = new Intl.NumberFormat('pt-BR', {
  style: 'currency', currency: 'BRL', notation: 'compact', maximumFractionDigits: 0,
})
const fmtFull = new Intl.NumberFormat('pt-BR', {
  style: 'currency', currency: 'BRL', maximumFractionDigits: 0,
})

const hasData = computed(() => props.data.length >= 2)

const plot = computed(() => ({
  w: Math.max(width.value - PAD.left - PAD.right, 1),
  h: Math.max(HEIGHT - PAD.top - PAD.bottom, 1),
}))

/**
 * Domínio "redondo" do eixo Y: expande a faixa dos dados até múltiplos de um
 * passo legível, pra que toda marca nomeie um valor inteiro. Série constante
 * (ou toda zero) não tem faixa — abre uma artificial em volta do valor pra não
 * gerar divisão por zero.
 */
const domain = computed(() => {
  const values = props.data.map(d => d.value)
  let min = values.length ? Math.min(...values) : 0
  let max = values.length ? Math.max(...values) : 0

  if (min === max) {
    const pad = Math.abs(min) * 0.1 || 1
    min -= pad
    max += pad
  }

  const step = niceStep((max - min) / 4)
  return {
    min: Math.floor(min / step) * step,
    max: Math.ceil(max / step) * step,
    step,
  }
})

function niceStep(raw: number) {
  const mag = 10 ** Math.floor(Math.log10(Math.abs(raw) || 1))
  const norm = raw / mag
  const factor = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10
  return factor * mag
}

function xAt(i: number) {
  const n = props.data.length
  if (n <= 1) return PAD.left
  return PAD.left + (plot.value.w * i) / (n - 1)
}

function yAt(value: number) {
  const { min, max } = domain.value
  const span = max - min || 1
  return PAD.top + plot.value.h * (1 - (value - min) / span)
}

const points = computed(() =>
  props.data.map((d, i) => ({ ...d, i, x: xAt(i), y: yAt(d.value) })),
)

const linePath = computed(() =>
  points.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${r(p.x)},${r(p.y)}`).join(' '),
)

const areaPath = computed(() => {
  if (!points.value.length) return ''
  const base = PAD.top + plot.value.h
  const first = points.value[0]!
  const last = points.value[points.value.length - 1]!
  return `${linePath.value} L${r(last.x)},${r(base)} L${r(first.x)},${r(base)} Z`
})

const yTicks = computed(() => {
  const { min, max, step } = domain.value
  const out: { value: number; y: number; label: string }[] = []
  for (let v = min; v <= max + step / 2; v += step) {
    out.push({ value: v, y: yAt(v), label: fmtCompact.format(v) })
  }
  return out
})

/**
 * Com muitos meses os rótulos se sobrepõem, então mostra um subconjunto
 * espaçado — sempre incluindo o primeiro e o último, que são os que ancoram a
 * leitura do período.
 */
const xTicks = computed(() => {
  const n = points.value.length
  const stride = Math.max(1, Math.ceil(n / MAX_X_LABELS))
  return points.value
    .filter((_, i) => i % stride === 0 || i === n - 1)
    .map(p => ({ x: p.x, label: p.date }))
})

const hovered = computed(() =>
  hoverIdx.value === null ? null : points.value[hoverIdx.value] ?? null,
)

const tooltipStyle = computed(() => {
  if (!hovered.value) return {}
  const pct = (hovered.value.x / width.value) * 100
  return {
    left: `${Math.min(Math.max(pct, 12), 88)}%`,
    top: `${hovered.value.y}px`,
  }
})

const ariaLabel = computed(() => {
  if (!hasData.value) return ''
  const first = props.data[0]!
  const last = props.data[props.data.length - 1]!
  return `Evolução do patrimônio de ${first.date} a ${last.date}: de ${fmtFull.format(first.value)} para ${fmtFull.format(last.value)}.`
})

function r(n: number) {
  return Number.isFinite(n) ? Math.round(n * 100) / 100 : 0
}

function onMove(e: MouseEvent) {
  const svg = e.currentTarget as SVGSVGElement
  const rect = svg.getBoundingClientRect()
  if (!rect.width || props.data.length < 2) return

  // do pixel da tela para a coordenada do viewBox, daí para o índice do ponto
  const vx = ((e.clientX - rect.left) / rect.width) * width.value
  const ratio = (vx - PAD.left) / plot.value.w
  const idx = Math.round(ratio * (props.data.length - 1))
  hoverIdx.value = Math.min(Math.max(idx, 0), props.data.length - 1)
}

let observer: ResizeObserver | null = null

function measure() {
  if (hostEl.value?.clientWidth) width.value = hostEl.value.clientWidth
}

onMounted(() => {
  measure()
  if (typeof ResizeObserver !== 'undefined' && hostEl.value) {
    observer = new ResizeObserver(measure)
    observer.observe(hostEl.value)
  }
})

onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
.timeline-host {
  position: relative;
  width: 100%;
  height: 200px;
}

.timeline-svg {
  width: 100%;
  height: 100%;
  display: block;
  overflow: visible;
}

.grid-line {
  stroke: rgba(255, 255, 255, 0.04);
  stroke-width: 1;
}

.axis-label {
  font-family: 'Space Grotesk', monospace;
  font-size: 10px;
  fill: var(--t4);
}

.timeline-line {
  fill: none;
  stroke: var(--blue);
  stroke-width: 2;
  stroke-linejoin: round;
  stroke-linecap: round;
}

.grad-top {
  stop-color: var(--blue);
  stop-opacity: 0.18;
}

.grad-bottom {
  stop-color: var(--blue);
  stop-opacity: 0;
}

.active-dot {
  fill: var(--blue);
  stroke: var(--bg);
  stroke-width: 2;
}

.timeline-tooltip {
  position: absolute;
  transform: translate(-50%, calc(-100% - 12px));
  pointer-events: none;
  padding: 8px 12px;
  background: var(--sf-hi);
  border: 1px solid var(--bd);
  border-radius: 6px;
  font-family: 'Space Grotesk', monospace;
  font-size: 0.72rem;
  line-height: 1.5;
  white-space: nowrap;
  z-index: 2;
}

.tt-date {
  color: var(--t2);
  font-size: 0.62rem;
  margin-bottom: 2px;
}

.tt-value {
  color: var(--blue);
}

.timeline-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  padding: 0 24px;
  text-align: center;
  color: var(--t3);
  font-size: 13px;
  line-height: 1.5;
}
</style>
