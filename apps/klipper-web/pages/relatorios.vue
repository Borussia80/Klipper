<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;z-index:10">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Relatórios</div>

        <!-- Month nav (only visible on tab mensal) -->
        <div v-if="tab === 'mensal'" style="margin-left:auto;display:flex;align-items:center;gap:4px">
          <button class="nav-btn" aria-label="Mês anterior" @click="prevMonth">‹</button>
          <span style="font-size:12px;color:var(--t2);min-width:96px;text-align:center">{{ monthLabel }}</span>
          <button class="nav-btn" :disabled="isCurrentMonth" aria-label="Próximo mês" @click="nextMonth">›</button>
        </div>
      </div>

      <!-- Tab switcher -->
      <div class="tab-bar">
        <button
          class="tab-btn"
          :class="{ active: tab === 'mensal' }"
          @click="tab = 'mensal'"
        >Mensal</button>
        <button
          class="tab-btn"
          :class="{ active: tab === 'patrimonio' }"
          @click="tab = 'patrimonio'"
        >Patrimônio</button>
      </div>
    </div>

    <div style="padding:0 20px 32px">

      <!-- ── TAB MENSAL ──────────────────────────────────────────── -->
      <template v-if="tab === 'mensal'">
        <!-- Summary tiles -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0">
          <div class="tile">
            <div class="plbl" style="margin-bottom:4px">Gastos</div>
            <div class="mono" style="font-size:16px;font-weight:500;color:var(--alert)">
              {{ isLoading ? '—' : formatBRL(monthly?.total_debits ?? 0) }}
            </div>
          </div>
          <div class="tile">
            <div class="plbl" style="margin-bottom:4px">Receitas</div>
            <div class="mono" style="font-size:16px;font-weight:500;color:var(--ok)">
              {{ isLoading ? '—' : formatBRL(monthly?.total_credits ?? 0) }}
            </div>
          </div>
          <div class="tile">
            <div class="plbl" style="margin-bottom:4px">Saldo</div>
            <div class="mono" style="font-size:16px;font-weight:500" :class="netClass">
              {{ isLoading ? '—' : formatBRL(monthly?.net ?? 0) }}
            </div>
          </div>
        </div>

        <!-- Category breakdown -->
        <div style="margin-bottom:8px;font-size:11px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.06em">
          Gastos por categoria
        </div>

        <template v-if="isLoading">
          <UiSkeletonCard v-for="n in 5" :key="n" style="margin-bottom:6px" />
        </template>
        <template v-else-if="!monthly?.by_category?.length">
          <div style="padding:40px 0;text-align:center;color:var(--t4);font-size:13px">
            Nenhum gasto registrado neste período.
          </div>
        </template>
        <template v-else>
          <div
            v-for="cat in monthly.by_category"
            :key="String(cat.category_id)"
            class="cat-row"
          >
            <div class="cat-icon">{{ cat.category_icon ?? '📦' }}</div>
            <div style="flex:1;min-width:0">
              <div style="font-size:13px;font-weight:500;color:var(--t1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                {{ cat.category_name }}
              </div>
              <div style="font-size:11px;color:var(--t4);margin-top:2px">{{ cat.count }} lançamento{{ cat.count !== 1 ? 's' : '' }}</div>
            </div>
            <div class="mono" style="font-size:13px;font-weight:500;color:var(--t1)">{{ formatBRL(cat.total) }}</div>
          </div>
        </template>
      </template>

      <!-- ── TAB PATRIMÔNIO ─────────────────────────────────────── -->
      <template v-else>
        <!-- Net worth hero -->
        <div class="tile nw-hero">
          <div class="plbl" style="margin-bottom:6px">Patrimônio Líquido</div>
          <div class="mono" style="font-size:26px;font-weight:600;color:var(--t1)">
            {{ isLoading ? '—' : formatBRL(netWorth?.net_worth ?? 0) }}
          </div>
        </div>

        <!-- Breakdown tiles -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px">
          <div class="tile">
            <div class="plbl" style="margin-bottom:4px">Contas</div>
            <div class="mono" style="font-size:16px;font-weight:500;color:var(--blue)">
              {{ isLoading ? '—' : formatBRL(netWorth?.accounts_total ?? 0) }}
            </div>
          </div>
          <div class="tile">
            <div class="plbl" style="margin-bottom:4px">Investimentos</div>
            <div class="mono" style="font-size:16px;font-weight:500;color:var(--blue)">
              {{ isLoading ? '—' : formatBRL(netWorth?.investments_cost ?? 0) }}
            </div>
          </div>
        </div>

        <template v-if="isLoading">
          <UiSkeletonCard v-for="n in 4" :key="n" style="margin-bottom:6px" />
        </template>
        <template v-else>
          <!-- Accounts list -->
          <div style="margin-bottom:8px;font-size:11px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.06em">
            Contas
          </div>
          <div
            v-for="acc in netWorth?.accounts"
            :key="acc.id"
            class="cat-row"
          >
            <div class="cat-icon">🏦</div>
            <div style="flex:1;min-width:0;font-size:13px;font-weight:500;color:var(--t1)">{{ acc.name }}</div>
            <div class="mono" style="font-size:13px;font-weight:500;color:var(--t1)">{{ formatBRL(acc.balance) }}</div>
          </div>

          <!-- Investments by type -->
          <div style="margin:16px 0 8px;font-size:11px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.06em">
            Investimentos por tipo
          </div>
          <div
            v-for="inv in netWorth?.investments_by_type"
            :key="inv.investment_type"
            class="cat-row"
          >
            <div class="cat-icon">📈</div>
            <div style="flex:1;min-width:0;font-size:13px;font-weight:500;color:var(--t1)">{{ investmentLabel(inv.investment_type) }}</div>
            <div class="mono" style="font-size:13px;font-weight:500;color:var(--t1)">{{ formatBRL(inv.total_cost) }}</div>
          </div>

          <div
            v-if="!netWorth?.accounts?.length && !netWorth?.investments_by_type?.length"
            style="padding:40px 0;text-align:center;color:var(--t4);font-size:13px"
          >
            Nenhum ativo registrado.
          </div>
        </template>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })

const { monthly, netWorth, isLoading, fetchMonthly, fetchNetWorth } = useReports()
const { formatBRL } = useFormatters()

const now = new Date()
const activeYear = ref(now.getFullYear())
const activeMonth = ref(now.getMonth() + 1)
const tab = ref<'mensal' | 'patrimonio'>('mensal')

const monthLabel = computed(() =>
  new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' }).format(
    new Date(activeYear.value, activeMonth.value - 1),
  )
)

const isCurrentMonth = computed(() => {
  const n = new Date()
  return activeYear.value === n.getFullYear() && activeMonth.value === n.getMonth() + 1
})

const netClass = computed(() => {
  const v = monthly.value?.net ?? 0
  return v >= 0 ? 'val-positive' : 'val-negative'
})

function prevMonth() {
  if (activeMonth.value === 1) {
    activeMonth.value = 12
    activeYear.value--
  } else {
    activeMonth.value--
  }
}

function nextMonth() {
  if (isCurrentMonth.value) return
  if (activeMonth.value === 12) {
    activeMonth.value = 1
    activeYear.value++
  } else {
    activeMonth.value++
  }
}

const INVESTMENT_LABELS: Record<string, string> = {
  stock: 'Ações',
  fii: 'FIIs',
  bond: 'Renda Fixa',
  crypto: 'Cripto',
  other: 'Outros',
}

function investmentLabel(type: string): string {
  return INVESTMENT_LABELS[type] ?? type
}

watch([activeYear, activeMonth], ([y, m]) => {
  if (tab.value === 'mensal') fetchMonthly(y, m)
})

watch(tab, (t) => {
  if (t === 'mensal') fetchMonthly(activeYear.value, activeMonth.value)
  else fetchNetWorth()
})

onMounted(() => {
  fetchMonthly(activeYear.value, activeMonth.value)
  fetchNetWorth()
})
</script>

<style scoped>
.tab-bar {
  display: flex;
  gap: 4px;
}

.tab-btn {
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--bd2);
  background: transparent;
  color: var(--t3);
  cursor: pointer;
  transition: background .12s, color .12s, border-color .12s;
}

.tab-btn.active {
  background: var(--blue);
  color: #fff;
  border-color: var(--blue);
}

.nav-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--r);
  border: 1px solid var(--bd2);
  background: var(--sf);
  color: var(--t2);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: background .12s;
}

.nav-btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.tile {
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 8px;
  padding: 12px;
}

.nw-hero {
  margin: 20px 0 10px;
  padding: 20px;
}

.cat-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 8px;
  margin-bottom: 6px;
}

.cat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--ly);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}
</style>
