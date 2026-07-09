<template>
  <div>
    <!-- Cockpit hero -->
    <div style="padding:32px 24px 0">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:28px">
        <div class="mono" style="font-size:10px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--t4)">{{ currentMonthLabel() }} · {{ now.getDate() }} · {{ now.toLocaleDateString('pt-BR', { weekday: 'long' }) }}</div>
        <div class="sel-wrap" style="width:170px">
          <select v-model="activeMemberId" class="fi fi-sel" style="padding-top:6px;padding-bottom:6px" aria-label="Filtrar por portador">
            <option :value="undefined">Todos os portadores</option>
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
          </select>
          <span class="sel-caret" aria-hidden="true">▾</span>
        </div>
      </div>

      <div class="mono" style="font-size:10px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:rgba(13,184,120,0.55);margin-bottom:10px">Livre para gastar</div>
      <div class="mono" style="font-size:80px;font-weight:100;letter-spacing:-.04em;line-height:.88;color:var(--ok);filter:drop-shadow(0 0 28px rgba(13,184,120,0.18))">{{ formatBRL(totalBalance) }}</div>

      <div style="margin-top:22px;display:flex;align-items:center;gap:14px">
        <div style="flex:1;height:1.5px;background:rgba(13,184,120,0.1);border-radius:1px">
          <div style="width:59%;height:100%;background:rgba(13,184,120,0.4);border-radius:1px"></div>
        </div>
        <span class="mono" style="font-size:10px;color:var(--t4);white-space:nowrap">59% · R$ 8.180 caixa</span>
      </div>
      <div style="margin-top:7px;font-size:11px;color:var(--t4)">{{ formatBRL(totalDebits) }} gastos · {{ formatBRL(totalCredits) }} recebidos</div>
    </div>

    <!-- Insight -->
    <div style="margin:10px 20px 0;padding:14px 18px;background:var(--sf);border:1px solid var(--bd2);border-radius:10px;display:flex;align-items:flex-start;gap:12px">
      <div style="flex-shrink:0;margin-top:1px;color:var(--warn)"><UiAppIcon name="info" :size="18" /></div>
      <div>
        <div style="font-size:13px;color:var(--t1);font-weight:500;margin-bottom:3px">Você está no caminho certo</div>
        <div style="font-size:12px;color:var(--t3);line-height:1.55">Taxa de poupança de {{ savingsRate }}% em {{ currentMonthLabel() }}.</div>
      </div>
    </div>

    <!-- Alertas -->
    <div style="padding:0 20px;margin-top:24px">
      <div style="font-size:10px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--t4);font-family:'JetBrains Mono',monospace;margin-bottom:10px">Atenção necessária</div>

      <template v-if="budgetAlerts.length">
        <div v-for="alert in budgetAlerts" :key="alert.budget_id" style="border-left:3px solid var(--warn);padding:13px 16px;border-radius:0 8px 8px 0;background:rgba(229,144,16,0.04);margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:16px">
            <div>
              <div style="font-size:13px;font-weight:500;color:var(--t1)">{{ alert.category_name }}</div>
              <div style="font-size:11px;color:var(--t3);margin-top:2px">{{ Math.round(alert.pct_used) }}% do orçamento usado</div>
            </div>
            <div style="text-align:right;flex-shrink:0">
              <div class="mono" style="font-size:13px;font-weight:500;color:var(--warn)">{{ formatBRL(alert.remaining) }} restante</div>
              <NuxtLink to="/orcamento" style="font-size:10px;color:var(--blue);cursor:pointer;margin-top:3px">ver orçamento →</NuxtLink>
            </div>
          </div>
        </div>
      </template>
      <div v-else style="padding:16px 0;text-align:center;color:var(--t4);font-size:12px">
        Nenhum alerta de orçamento.
      </div>
    </div>

    <!-- Split fixo × cartão × variável -->
    <div v-if="donutData.length" style="padding:0 20px;margin-top:24px">
      <div style="font-size:10px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--t4);font-family:'JetBrains Mono',monospace;margin-bottom:2px">Fixo × Cartão × Variável</div>
      <div style="font-size:11px;color:var(--t4);margin-bottom:10px">Total categorizado em {{ currentMonthLabel() }}</div>
      <ChartsAlocacaoDonut :data="donutData" :total="naturezaSplit?.total ?? 0" />
      <div style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
        <div v-for="row in donutData" :key="row.name" style="display:flex;align-items:center;justify-content:space-between;gap:12px">
          <div style="display:flex;align-items:center;gap:8px">
            <span style="width:8px;height:8px;border-radius:50%;flex-shrink:0" :style="{ background: row.color }"></span>
            <span style="font-size:12px;color:var(--t2)">{{ row.name }}</span>
          </div>
          <span class="mono" style="font-size:12px;color:var(--t1)">{{ formatBRL(row.value) }}</span>
        </div>
      </div>
    </div>

    <!-- Lançamentos recentes -->
    <div style="padding:0 20px;margin-top:24px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
        <div style="font-size:10px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--t4);font-family:'JetBrains Mono',monospace">Lançamentos recentes</div>
        <NuxtLink to="/transacoes" style="font-size:11px;color:var(--blue);text-decoration:none;cursor:pointer">ver todos →</NuxtLink>
      </div>

      <!-- Skeleton while loading (wire-up point for real data fetch) -->
      <template v-if="isLoading">
        <UiSkeletonCard v-for="n in 4" :key="n" style="margin-bottom:8px" />
      </template>

      <template v-else>
        <div v-for="tx in recentTransactions" :key="tx.id" class="txr">
          <div style="width:32px;height:32px;border-radius:8px;background:rgba(43,125,244,0.1);display:flex;align-items:center;justify-content:center;color:var(--blue);flex-shrink:0">
            <UiAppIcon :name="tx.transaction_type === 'credit' ? 'income' : 'expense'" :size="16" />
          </div>
          <div>
            <div style="font-size:13px;font-weight:500;color:var(--t1)">{{ tx.description }}</div>
            <div style="font-size:11px;color:var(--t3);margin-top:1px">{{ fmtDate(tx.occurred_on) }}</div>
          </div>
          <span class="mono" style="font-size:13px;" :style="tx.transaction_type === 'credit' ? 'color:var(--ok)' : 'color:var(--t2)'">
            {{ tx.transaction_type === 'credit' ? '+' : '-' }} {{ formatBRL(parseFloat(tx.amount)) }}
          </span>
        </div>
        <div v-if="!recentTransactions.length" style="padding:32px 0;text-align:center;color:var(--t4);font-size:13px">
          Nenhum lançamento este mês.
        </div>
      </template>
    </div>

    <!-- Kira AI -->
    <div style="margin:20px 20px 32px;padding:16px;background:var(--sf);border:1px solid var(--bd2);border-radius:10px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
        <img src="/klipper-mark.png" style="width:18px;height:18px;border-radius:4px;display:block;flex-shrink:0" alt="">
        <span style="font-size:12px;font-weight:600;color:var(--t2)">Kira pode ajudar</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">
        <button class="pill">Como estou gastando?</button>
        <button class="pill">Posso economizar onde?</button>
        <button class="pill">Resumo do mês</button>
        <button class="pill">Prever próximos meses</button>
      </div>
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

const savingsRate = computed(() => {
  if (!totalCredits.value || totalCredits.value === 0) return 0
  return Math.round(((totalCredits.value - totalDebits.value) / totalCredits.value) * 100)
})

const budgetAlerts = computed(() =>
  summary.value
    .filter(b => b.amount_limit > 0 && b.pct_used > 80)
    .slice(0, 2)
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
</style>
