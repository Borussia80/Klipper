<template>
  <div class="dash" style="max-width:1160px">
    <div class="page-head">
      <div>
        <div class="page-title">Painel</div>
        <div class="page-sub">{{ dateLabel }}</div>
      </div>
      <div style="display:flex;gap:10px">
        <div class="pill" style="cursor:default">{{ currentMonthLabel() }}</div>
        <div class="pill brass sel-wrap">
          <select v-model="activeMemberId" class="fi-sel" aria-label="Filtrar por portador">
            <option :value="undefined">Todos os portadores</option>
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
          </select>
          <span class="sel-caret" aria-hidden="true">▾</span>
        </div>
      </div>
    </div>

    <!-- Error banner -->
    <div v-if="dashboardError" role="alert" style="background:var(--ald);border:1px solid var(--alert);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px">
      {{ dashboardError }}
    </div>

    <!-- Loading skeleton -->
    <template v-if="dashboardLoading">
      <UiSkeletonCard v-for="n in 4" :key="n" style="margin-bottom:8px" />
    </template>

    <!-- Empty state -->
    <div v-else-if="!hasData" style="padding:48px 0;text-align:center;color:var(--t4);font-size:13px">
      Nenhum lançamento neste mês ainda.
      <br />
      <NuxtLink class="btn btn-p" style="margin-top:12px;display:inline-block" to="/importar">Importar extrato</NuxtLink>
    </div>

    <template v-else>
      <UiInstrumentReadout
        style="margin-bottom:20px"
        label="Resultado do mês · operacional"
        :net-value="netResult"
        :formatted-value="formatBRL(netResult)"
        :spent-ratio="spentRatio"
        :detail="heroDetail"
      />

      <UiDebtAlarmBanner
        v-if="showDebtAlarm"
        style="margin-bottom:20px"
        :row="debtRanking!.cards[0]"
      />

      <div v-if="kpiCount" class="kpi-grid" :style="{ gridTemplateColumns: `repeat(${kpiCount},1fr)` }">
        <UiKpiCard
          v-if="incomeHighlight"
          :label="incomeCategory?.name ?? 'Maior entrada do mês'"
          icon="income"
          :value="formatBRL(parseFloat(incomeHighlight.amount))"
          :chip-text="`recebido em ${fmtDate(incomeHighlight.occurred_on)}`"
        />
        <UiKpiCard
          v-if="fixoRow"
          label="Compromissos fixos"
          icon="home"
          :value="formatBRL(fixoRow.total)"
          :chip-text="fixoPct !== null ? `${Math.round(fixoPct * 100)}% da renda` : undefined"
          :chip-tone="commitmentTone(fixoPct)"
        />
        <UiKpiCard
          v-if="cartaoRow"
          label="Cartões & parcelas"
          icon="card"
          :value="formatBRL(cartaoRow.total)"
          :chip-text="cartaoPct !== null ? `${Math.round(cartaoPct * 100)}% da renda` : undefined"
          :chip-tone="commitmentTone(cartaoPct)"
        />
      </div>

      <div v-if="colsCount" class="cols" :style="{ gridTemplateColumns: colsCount === 2 ? '1fr 1fr' : '1fr' }">
        <div v-if="splitBars.length" class="card">
          <div class="card-h">
            <span class="card-title">Fixo × Cartão × Variável</span>
            <NuxtLink class="link" to="/orcamento">Relatório →</NuxtLink>
          </div>
          <div v-for="bar in splitBars" :key="bar.name" class="split-row">
            <span class="split-dot" :style="{ background: bar.color }"></span>
            <span class="split-name">{{ bar.name }}</span>
            <span class="split-track"><span class="f" :style="{ width: bar.pct + '%', background: bar.color }"></span></span>
            <span class="split-val mono">{{ formatBRL(bar.value) }}</span>
            <span class="split-pct mono">{{ Math.round(bar.pct) }}%</span>
          </div>
        </div>

        <div v-if="debtRanking?.cards.length" class="card">
          <div class="card-h">
            <span class="card-title">Prioridade de quitação</span>
            <NuxtLink class="link" to="/contas">Todos os cartões →</NuxtLink>
          </div>
          <UiDebtRankingCard
            v-for="(card, i) in debtRanking.cards"
            :key="card.account_id"
            :rank="i"
            :row="card"
          />
        </div>
      </div>

      <div
        v-for="row in reimbursementCoverage?.categories ?? []"
        :key="row.category_id"
        class="card"
        style="margin-bottom:14px"
      >
        <div class="card-h">
          <span class="card-title">{{ row.category_name }} · cobertura {{ row.reimbursed_by_category_name }}</span>
          <span v-if="row.coverage_pct !== null" class="chip" :class="row.alert ? 'alert' : 'ok'">
            {{ Math.round(row.coverage_pct) }}% coberto
          </span>
        </div>
        <div class="split-row">
          <span class="split-dot" style="background:var(--alert)"></span>
          <span class="split-name">Gasto no mês</span>
          <span class="split-track"><span class="f" style="width:100%;background:var(--bd-hi)"></span></span>
          <span class="split-val mono">{{ formatBRL(row.spent) }}</span>
          <span class="split-pct mono">100%</span>
        </div>
        <div class="split-row">
          <span class="split-dot" style="background:var(--ok)"></span>
          <span class="split-name">Reembolsado</span>
          <span class="split-track"><span class="f" :style="{ width: (row.coverage_pct ?? 0) + '%', background: 'var(--ok)' }"></span></span>
          <span class="split-val mono">{{ formatBRL(row.reimbursed) }}</span>
          <span class="split-pct mono">{{ row.coverage_pct !== null ? Math.round(row.coverage_pct) + '%' : '—' }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })

const {
  transactions,
  totalDebits,
  totalCredits,
  fetchTransactions,
  isLoading: transactionsLoading,
  error: transactionsError,
} = useTransactions()
const { members, fetchMembers, error: membersError } = useMembers()
const { formatBRL, currentMonthLabel } = useFormatters()
const {
  naturezaSplit,
  fetchNaturezaSplit,
  debtRanking,
  fetchDebtRanking,
  reimbursementCoverage,
  fetchReimbursementCoverage,
  isLoading: reportsLoading,
  error: reportsError,
} = useReports()
const { categories, fetchCategories, error: categoriesError } = useCategories()

const dashboardLoading = computed(() => transactionsLoading.value || reportsLoading.value)
const dashboardError = computed(
  () => transactionsError.value || reportsError.value || categoriesError.value || membersError.value
)
const hasData = computed(() => transactions.value.length > 0)

const now = new Date()
const activeMemberId = ref<number | undefined>(undefined)

const dateLabel = computed(() => {
  const weekday = new Intl.DateTimeFormat('pt-BR', { weekday: 'long' }).format(now)
  const full = new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' }).format(now)
  return `${weekday.charAt(0).toUpperCase() + weekday.slice(1)}, ${full} · ciclo em andamento`
})

function loadTransactions() {
  fetchTransactions({ year: now.getFullYear(), month: now.getMonth() + 1, member_id: activeMemberId.value })
}

function loadNaturezaSplit() {
  fetchNaturezaSplit(now.getFullYear(), now.getMonth() + 1, activeMemberId.value)
}

onMounted(() => {
  fetchMembers()
  fetchCategories()
  loadTransactions()
  loadNaturezaSplit()
  fetchDebtRanking()
  fetchReimbursementCoverage(now.getFullYear(), now.getMonth() + 1)
})

watch(activeMemberId, () => {
  loadTransactions()
  loadNaturezaSplit()
})

function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' }).format(
    new Date(iso + 'T12:00:00')
  )
}

function commitmentTone(pct: number | null): 'warn' | 'alert' | 'neutral' {
  if (pct === null) return 'neutral'
  if (pct >= 0.7) return 'alert'
  if (pct >= 0.4) return 'warn'
  return 'neutral'
}

const netResult = computed(() => totalCredits.value - totalDebits.value)

const spentRatio = computed(() => (totalCredits.value > 0 ? totalDebits.value / totalCredits.value : 0))

const heroDetail = computed(() => {
  if (totalCredits.value <= 0 && totalDebits.value <= 0) return undefined
  return `de ${formatBRL(totalCredits.value)} em entradas contra ${formatBRL(totalDebits.value)} em saídas`
})

const showDebtAlarm = computed(() => isDebtAlarmVisible(debtRanking.value))

const incomeHighlight = computed(() => pickIncomeHighlight(transactions.value, categories.value))
const incomeCategory = computed(() => categories.value.find((c) => c.id === incomeHighlight.value?.category_id) ?? null)

const fixoRow = computed(() => naturezaSplit.value?.by_natureza.find((r) => r.natureza === 'fixo' && r.total > 0) ?? null)
const cartaoRow = computed(() => naturezaSplit.value?.by_natureza.find((r) => r.natureza === 'cartao_parcelamento' && r.total > 0) ?? null)

const fixoPct = computed(() => pctOfIncome(fixoRow.value?.total ?? 0, totalCredits.value))
const cartaoPct = computed(() => pctOfIncome(cartaoRow.value?.total ?? 0, totalCredits.value))

const kpiCount = computed(() => [incomeHighlight.value, fixoRow.value, cartaoRow.value].filter(Boolean).length)

const splitBars = computed(() =>
  mapNaturezaSplitToBars(
    (naturezaSplit.value?.by_natureza ?? []).filter((r) => r.total > 0),
    { fixo: 'var(--sea)', cartao_parcelamento: 'var(--alert)', variavel: 'var(--brass)' }
  )
)

const colsCount = computed(() =>
  [splitBars.value.length > 0, (debtRanking.value?.cards.length ?? 0) > 0].filter(Boolean).length
)
</script>

<style scoped>
.page-head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 22px; }
.page-title { font-family: 'Space Grotesk'; font-size: 22px; font-weight: 600; letter-spacing: -.01em; }
.page-sub { color: var(--t3); font-size: 13px; margin-top: 3px; }

.pill {
  background: var(--sf); border: 1px solid var(--bd); border-radius: var(--r-sm);
  padding: 7px 13px; font-size: 13px; color: var(--t2); font-weight: 500;
  display: flex; align-items: center; gap: 8px;
}
.pill.brass { border-color: var(--brass-dim); color: var(--brass); }

.sel-wrap { position: relative; }
.fi-sel {
  -webkit-appearance: none; appearance: none; background: none; border: none;
  color: inherit; font: inherit; cursor: pointer; padding-right: 16px;
}
.sel-caret { position: absolute; right: 0; top: 50%; transform: translateY(-50%); font-size: 11px; pointer-events: none; }

.kpi-grid { display: grid; gap: 14px; margin-bottom: 20px; }
.cols { display: grid; gap: 14px; margin-bottom: 14px; }

.card {
  background: var(--sf); border: 1px solid var(--bd); border-radius: var(--r);
  padding: 17px 18px; transition: border-color .14s;
}
.card:hover { border-color: var(--bd-hi); }
.card-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.card-title { font-family: 'Space Grotesk'; font-size: 15px; font-weight: 600; }
.link { color: var(--sea); font-size: 12.5px; text-decoration: none; font-weight: 500; }

.split-row { display: flex; align-items: center; gap: 12px; margin-bottom: 13px; }
.split-row:last-child { margin-bottom: 0; }
.split-dot { width: 9px; height: 9px; border-radius: 3px; flex: none; }
.split-name { font-size: 13px; color: var(--t2); width: 150px; flex: none; }
.split-track { flex: 1; height: 7px; background: var(--bg); border-radius: 4px; overflow: hidden; }
.split-track .f { height: 100%; border-radius: 4px; }
.split-val { font-size: 13px; font-weight: 600; width: 88px; text-align: right; flex: none; }
.split-pct { font-size: 12px; color: var(--t3); width: 42px; text-align: right; flex: none; }

.chip { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 20px; font-family: 'Space Grotesk'; }
.chip.ok { background: rgba(67,197,158,0.13); color: var(--ok); }
.chip.warn { background: rgba(230,180,76,0.14); color: var(--warn); }
.chip.alert { background: rgba(232,115,90,0.14); color: var(--alert); }

@media (max-width: 920px) {
  .kpi-grid, .cols { grid-template-columns: 1fr !important; }
}
</style>
