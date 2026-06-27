<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;display:flex;align-items:center;gap:12px;z-index:10">
      <div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Investimentos</div>
        <div style="font-size:11px;color:var(--t3)">Portfólio · 5 ativos</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
        <div style="text-align:right">
          <div class="mono" style="font-size:16px;font-weight:500;color:var(--t1);line-height:1.2">R$ 187.400</div>
          <div style="font-size:11px;color:var(--ok)">▲ +14,2% total</div>
        </div>
        <div style="width:1px;height:24px;background:var(--bd2);flex-shrink:0"></div>
        <button class="btn btn-g" @click="open('novo-aporte')">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          Novo aporte
        </button>
      </div>
    </div>

    <div style="padding:0 20px 32px">
      <!-- Allocation bar -->
      <div style="margin-top:20px;background:var(--sf);border:1px solid var(--bd2);border-radius:10px;padding:18px 20px">
        <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'JetBrains Mono',monospace;margin-bottom:14px">Alocação por classe</div>
        <!-- Dynamic allocation bar -->
        <div v-if="portfolio" style="display:flex;border-radius:6px;overflow:hidden;height:8px;gap:2px;margin-bottom:14px">
          <div
            v-for="seg in portfolio.by_type"
            :key="seg.investment_type"
            :style="`width:${seg.pct_of_portfolio}%;background:${typeColor(seg.investment_type)}`"
            :title="`${typeLabel(seg.investment_type)} ${seg.pct_of_portfolio}%`"
          />
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px 20px">
          <div v-for="seg in portfolio?.by_type ?? []" :key="seg.investment_type" style="display:flex;align-items:center;gap:6px">
            <div :style="`width:8px;height:8px;border-radius:2px;background:${typeColor(seg.investment_type)};flex-shrink:0`"></div>
            <span style="font-size:11px;color:var(--t2)">{{ typeLabel(seg.investment_type) }} <strong style="color:var(--t1)">{{ seg.pct_of_portfolio }}%</strong></span>
          </div>
        </div>
      </div>

      <!-- Holdings table header -->
      <div style="display:grid;grid-template-columns:40px 1fr auto;gap:12px;padding:12px 8px;margin:16px -8px 0;border-bottom:1px solid var(--bd)">
        <div></div>
        <div style="font-size:10px;font-weight:600;color:var(--t4);text-transform:uppercase;letter-spacing:.07em;font-family:'JetBrains Mono',monospace">Ativo</div>
        <div style="font-size:10px;font-weight:600;color:var(--t4);text-transform:uppercase;letter-spacing:.07em;font-family:'JetBrains Mono',monospace;text-align:right">Valor</div>
      </div>

      <UiSkeletonTransactionList v-if="isLoading" />
      <template v-else>
        <div v-for="inv in investments" :key="inv.id" class="hr">
          <div :style="`width:36px;height:36px;border-radius:8px;background:${typeColorAlpha(inv.investment_type)};display:flex;align-items:center;justify-content:center;flex-shrink:0`">
            <div :style="`width:8px;height:8px;border-radius:2px;background:${typeColor(inv.investment_type)}`"></div>
          </div>
          <div>
            <div style="font-size:13px;font-weight:600;color:var(--t1)">{{ inv.ticker || inv.name }}</div>
            <div style="font-size:11px;color:var(--t3)">{{ typeLabel(inv.investment_type) }} · {{ inv.quantity }} un.</div>
          </div>
          <div style="text-align:right">
            <div class="mono" style="font-size:13px;font-weight:500;color:var(--t1)">{{ formatBRL(parseFloat(inv.quantity) * parseFloat(inv.average_price)) }}</div>
          </div>
        </div>
        <div v-if="!investments.length" style="padding:40px 0;text-align:center;color:var(--t4);font-size:13px">
          Nenhum investimento cadastrado.
        </div>
      </template>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })
const { open } = useModal()
const { investments, portfolio, isLoading, fetchInvestments, fetchPortfolio } = useInvestments()
const { formatBRL } = useFormatters()

onMounted(() => { fetchInvestments(); fetchPortfolio() })

const TYPE_COLORS: Record<string, string> = {
  fixed_income: 'var(--ok)',
  stock:        'var(--warn)',
  etf:          'var(--blue)',
  fii:          'var(--pur)',
  crypto:       'var(--crypto)',
  other:        'var(--t4)',
}
const TYPE_LABELS: Record<string, string> = {
  fixed_income: 'Renda Fixa',
  stock:        'Ações BR',
  etf:          'ETF',
  fii:          'FIIs',
  crypto:       'Cripto',
  other:        'Outros',
}

function typeColor(t: string) { return TYPE_COLORS[t] ?? 'var(--t4)' }
function typeColorAlpha(t: string) {
  const map: Record<string, string> = {
    fixed_income: 'rgba(13,184,120,0.12)', stock: 'rgba(229,144,16,0.12)',
    etf: 'rgba(43,125,244,0.12)', fii: 'rgba(124,92,245,0.12)',
    crypto: 'rgba(244,192,48,0.12)', other: 'rgba(128,128,128,0.12)',
  }
  return map[t] ?? 'rgba(128,128,128,0.12)'
}
function typeLabel(t: string) { return TYPE_LABELS[t] ?? t }
</script>
