<template>
  <div v-if="semMovimento" class="fm-empty" data-testid="fluxo-vazio">
    Nenhum lançamento nos últimos {{ points.length }} meses.
  </div>

  <div v-else class="fm" role="img" :aria-label="ariaLabel">
    <div
      v-for="p in colunas"
      :key="`${p.year}-${p.month}`"
      class="fm-col"
      :class="{ vazio: p.vazio }"
      data-testid="fluxo-mes"
      :data-mes="p.month"
    >
      <div class="fm-net" :class="{ neg: p.net < 0 }" data-testid="fluxo-net">
        {{ p.vazio ? '—' : formatBRLCompact(p.net) }}
      </div>

      <div class="fm-bars">
        <div
          v-if="p.total_credits > 0"
          class="fm-bar fm-in"
          data-testid="barra-entrada"
          :style="{ height: `${p.altIn}%` }"
          :title="`Entradas: ${formatBRL(p.total_credits)}`"
        />
        <div
          v-if="p.total_debits > 0"
          class="fm-bar fm-out"
          data-testid="barra-saida"
          :style="{ height: `${p.altOut}%` }"
          :title="`Saídas: ${formatBRL(p.total_debits)}`"
        />
      </div>

      <div class="fm-lbl">{{ p.label }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * FluxoMensal — entradas × saídas × resultado, um grupo de barras por mês.
 *
 * Mês sem lançamento continua ocupando a sua coluna: encostar março em janeiro
 * desenharia uma continuidade que o dado não tem. E a escala é a da janela
 * inteira, não a de cada coluna, senão dois meses de tamanhos muito diferentes
 * apareceriam com a mesma altura.
 */
import type { MonthlySeriesPoint } from '~/composables/useReports'

const props = defineProps<{ points: MonthlySeriesPoint[] }>()

const { formatBRL, formatBRLCompact } = useFormatters()

const MESES = [ 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez' ]

const teto = computed(() =>
  Math.max(...props.points.map((p: MonthlySeriesPoint) => Math.max(p.total_credits, p.total_debits)), 0)
)

const semMovimento = computed(() => teto.value <= 0)

const colunas = computed(() =>
  props.points.map((p: MonthlySeriesPoint) => ({
    ...p,
    label: MESES[p.month - 1] ?? String(p.month),
    vazio: p.total_credits === 0 && p.total_debits === 0,
    altIn: pct(p.total_credits),
    altOut: pct(p.total_debits),
  }))
)

function pct(valor: number): number {
  if (teto.value <= 0) return 0
  return Math.round((valor / teto.value) * 100)
}

const ariaLabel = computed(() => {
  const primeiro = colunas.value[0]
  const ultimo = colunas.value[colunas.value.length - 1]
  if (!primeiro || !ultimo) return ''
  return `Entradas e saídas de ${primeiro.label} a ${ultimo.label}. ` +
    colunas.value
      .map((c: (typeof colunas.value)[number]) => `${c.label}: ${c.vazio ? 'sem lançamento' : `resultado ${formatBRL(c.net)}`}`)
      .join('; ')
})
</script>

<style scoped>
.fm { display: flex; align-items: flex-end; gap: 10px; height: 168px; }
.fm-col { flex: 1; display: flex; flex-direction: column; height: 100%; min-width: 0; }
.fm-col.vazio { opacity: .5; }

.fm-net {
  font-family: 'Space Grotesk', monospace; font-size: 10px; color: var(--ok);
  text-align: center; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.fm-net.neg { color: var(--alert); }

.fm-bars { flex: 1; display: flex; align-items: flex-end; justify-content: center; gap: 3px; }
.fm-bar { width: 42%; max-width: 18px; border-radius: 2px 2px 0 0; min-height: 2px; }
.fm-in { background: var(--ok); }
.fm-out { background: var(--alert); }

.fm-lbl { font-size: 10px; color: var(--t3); text-align: center; margin-top: 6px; }

.fm-empty {
  display: flex; align-items: center; justify-content: center; height: 168px;
  color: var(--t3); font-size: 13px; text-align: center;
}
</style>
