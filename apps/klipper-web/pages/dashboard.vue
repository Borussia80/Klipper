<template>
  <div style="padding:32px 24px">
    <!-- Contexto + filtro -->
    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:32px">
      <div style="font-size:13px;color:var(--t3)">
        {{ currentMonthLabel() }} · {{ now.getDate() }} · {{ now.toLocaleDateString('pt-BR', { weekday: 'long' }) }}
      </div>
      <div class="sel-wrap" style="width:180px">
        <select v-model="activeMemberId" class="fi fi-sel" style="padding-top:6px;padding-bottom:6px" aria-label="Filtrar por portador">
          <option :value="undefined">Todos os portadores</option>
          <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>
        <span class="sel-caret" aria-hidden="true">▾</span>
      </div>
    </div>

    <!-- 1. Instrumento primário -->
    <UiInstrumentReadout
      label="Livre para gastar"
      :value="formatBRL(totalBalance)"
      :ratio="freeRatio"
      :detail="`${formatBRL(totalDebits)} gastos · ${formatBRL(totalCredits)} recebidos em ${currentMonthLabel()}`"
    />

    <!-- 2. Alarmes acionáveis -->
    <div style="margin-top:36px">
      <div class="slbl">Atenção necessária</div>

      <template v-if="budgetAlerts.length">
        <div
          v-for="alert in budgetAlerts"
          :key="alert.budget_id"
          :style="`border-left:3px solid var(${alert.pct_used > 100 ? '--alert' : '--warn'});padding:12px 16px;border-radius:0 8px 8px 0;background:var(--sf);margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;gap:16px`"
        >
          <div>
            <div style="font-size:14px;font-weight:500;color:var(--t1)">{{ alert.category_name }}</div>
            <div style="font-size:12px;color:var(--t3);margin-top:2px">
              {{ Math.round(alert.pct_used) }}% do orçamento usado<template v-if="alert.pct_used > 100"> — limite estourado</template>
            </div>
          </div>
          <div style="text-align:right;flex-shrink:0">
            <div class="mono" :style="`font-size:14px;font-weight:500;color:var(${alert.pct_used > 100 ? '--alert' : '--warn'})`">
              {{ formatBRL(alert.remaining) }} restante
            </div>
            <NuxtLink to="/orcamento" style="font-size:12px;color:var(--blue)">ver orçamento →</NuxtLink>
          </div>
        </div>
      </template>
      <div v-else style="padding:12px 0;color:var(--t3);font-size:13px">
        Nenhuma condição anormal — orçamentos dentro da faixa.
      </div>
    </div>

    <!-- 3. Detalhe sob demanda -->
    <details class="fold" style="margin-top:28px">
      <summary class="fold-summary">
        <span class="fold-caret" aria-hidden="true">▸</span>
        Fixo × Cartão × Variável
        <span v-if="naturezaSplit?.total" class="mono" style="margin-left:auto;font-size:12px;color:var(--t3)">{{ formatBRL(naturezaSplit.total) }}</span>
      </summary>
      <div style="padding:16px 0 8px">
        <template v-if="donutData.length">
          <ChartsAlocacaoDonut :data="donutData" :total="naturezaSplit?.total ?? 0" />
          <div style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
            <div v-for="row in donutData" :key="row.name" style="display:flex;align-items:center;justify-content:space-between;gap:12px">
              <div style="display:flex;align-items:center;gap:8px">
                <span style="width:8px;height:8px;border-radius:50%;flex-shrink:0" :style="{ background: row.color }"></span>
                <span style="font-size:13px;color:var(--t2)">{{ row.name }}</span>
              </div>
              <span class="mono" style="font-size:13px;color:var(--t1)">{{ formatBRL(row.value) }}</span>
            </div>
          </div>
        </template>
        <div v-else style="color:var(--t4);font-size:13px">Nada categorizado em {{ currentMonthLabel() }}.</div>
      </div>
    </details>

    <details class="fold">
      <summary class="fold-summary">
        <span class="fold-caret" aria-hidden="true">▸</span>
        Lançamentos recentes
        <NuxtLink to="/transacoes" style="margin-left:auto;font-size:12px;color:var(--blue)" @click.stop>ver todos →</NuxtLink>
      </summary>
      <div style="padding:8px 0">
        <template v-if="isLoading">
          <UiSkeletonCard v-for="n in 4" :key="n" style="margin-bottom:8px" />
        </template>
        <template v-else>
          <div v-for="tx in recentTransactions" :key="tx.id" class="txr">
            <div style="width:32px;height:32px;border-radius:8px;background:var(--ly);display:flex;align-items:center;justify-content:center;color:var(--t3);flex-shrink:0">
              <UiAppIcon :name="tx.transaction_type === 'credit' ? 'income' : 'expense'" :size="16" />
            </div>
            <div>
              <div style="font-size:14px;font-weight:500;color:var(--t1)">{{ tx.description }}</div>
              <div style="font-size:12px;color:var(--t3);margin-top:1px">{{ fmtDate(tx.occurred_on) }}</div>
            </div>
            <span class="mono" style="font-size:14px;color:var(--t2)">
              {{ tx.transaction_type === 'credit' ? '+' : '-' }} {{ formatBRL(parseFloat(tx.amount)) }}
            </span>
          </div>
          <div v-if="!recentTransactions.length" style="padding:24px 0;color:var(--t4);font-size:13px">
            Nenhum lançamento este mês.
          </div>
        </template>
      </div>
    </details>

    <!-- 4. Kira — uma linha discreta -->
    <div style="margin-top:28px;display:flex;align-items:center;flex-wrap:wrap;gap:6px">
      <span style="font-size:12px;color:var(--t4);margin-right:4px">Perguntar à Kira:</span>
      <button class="pill">Como estou gastando?</button>
      <button class="pill">Posso economizar onde?</button>
      <button class="pill">Resumo do mês</button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })

const { totalBalance, isLoading, fetchAccounts } = useAccounts()
const { transactions, totalDebits, totalCredits, fetchTransactions } = useTransactions()
const { members, fetchMembers } = useMembers()
const { formatBRL, currentMonthLabel } = useFormatters()
const { summary, fetchSummary } = useBudgets()
const { naturezaSplit, fetchNaturezaSplit } = useReports()
const chartTokens = useChartTokens()

const now = new Date()
const activeMemberId = ref<number | undefined>(undefined)

function loadTransactions() {
  fetchTransactions({ year: now.getFullYear(), month: now.getMonth() + 1, member_id: activeMemberId.value })
}

function loadNaturezaSplit() {
  fetchNaturezaSplit(now.getFullYear(), now.getMonth() + 1, activeMemberId.value)
}

onMounted(() => {
  fetchAccounts()
  fetchMembers()
  loadTransactions()
  fetchSummary(now.getFullYear(), now.getMonth() + 1)
  loadNaturezaSplit()
})

watch(activeMemberId, () => {
  loadTransactions()
  loadNaturezaSplit()
})

const NATUREZA_LABELS: Record<string, string> = {
  fixo: 'Fixo',
  cartao_parcelamento: 'Cartão/Parcelamento',
  variavel: 'Variável',
}

const donutData = computed(() => {
  const rows = naturezaSplit.value?.by_natureza ?? []
  return rows
    .filter(r => r.total > 0)
    .map(r => ({
      name: NATUREZA_LABELS[r.natureza] ?? r.natureza,
      value: r.total,
      color: r.natureza === 'fixo'
        ? chartTokens.value.blue
        : r.natureza === 'cartao_parcelamento'
          ? chartTokens.value.warn
          : chartTokens.value.ok,
    }))
})

const recentTransactions = computed(() => transactions.value.slice(0, 5))

// Fração da renda do mês ainda não gasta (barra de faixa do instrumento).
// Sem receita registrada, a faixa fica em zero — nada de número inventado.
const freeRatio = computed(() => {
  if (!totalCredits.value || totalCredits.value <= 0) return 0
  return 1 - totalDebits.value / totalCredits.value
})

const budgetAlerts = computed(() =>
  summary.value.filter(b => b.amount_limit > 0 && b.pct_used > 80)
)

function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' }).format(
    new Date(iso + 'T12:00:00')
  )
}
</script>

<style scoped>
.fi-sel {
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
  padding-right: 32px;
}

.sel-wrap {
  position: relative;
}

.sel-caret {
  position: absolute;
  right: 11px;
  top: 50%;
  transform: translateY(-60%);
  color: var(--t3);
  font-size: 12px;
  pointer-events: none;
  line-height: 1;
}

/* ── Seções colapsadas (disclosure progressivo) ── */
.fold {
  border-top: 1px solid var(--bd);
}

.fold-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--t3);
  cursor: pointer;
  list-style: none;
  user-select: none;
  transition: color 0.12s;
}
.fold-summary:hover { color: var(--t2); }
.fold-summary::-webkit-details-marker { display: none; }

.fold-caret {
  font-size: 11px;
  color: var(--t4);
  transition: transform 0.15s;
}
.fold[open] .fold-caret { transform: rotate(90deg); }
</style>
