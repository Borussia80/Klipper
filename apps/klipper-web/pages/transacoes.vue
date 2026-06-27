<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;display:flex;align-items:center;gap:12px;z-index:10">
      <div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Transações</div>
        <div style="font-size:11px;color:var(--t3)">Junho 2026 · 12 lançamentos</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:6px">
        <button class="pill on">Todos</button>
        <button class="pill">Entradas</button>
        <button class="pill">Saídas</button>
        <div style="width:1px;height:16px;background:var(--bd2);margin:0 2px;flex-shrink:0"></div>
        <button class="btn btn-g" @click="open('novo-lancamento')">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          Adicionar
        </button>
      </div>
    </div>

    <div style="padding:0 20px 32px">
      <!-- Skeleton while loading (wire-up point for real data fetch) -->
      <UiSkeletonTransactionList v-if="isLoading" :count="4" />

      <template v-else>
        <div v-if="!transactions.length" style="padding:60px 0;text-align:center;color:var(--t4);font-size:13px">
          Nenhum lançamento no período.
        </div>

        <template v-for="[date, txns] in groupedTransactions" :key="date">
          <div class="gh">
            <span class="gl">{{ fmtDate(date) }}</span>
            <span class="gr"></span>
            <span class="gc">{{ txns.length }} lançamento{{ txns.length !== 1 ? 's' : '' }}</span>
          </div>

          <div v-for="t in txns" :key="t.id" class="txr">
            <div style="width:36px;height:36px;border-radius:9px;background:rgba(43,125,244,0.1);display:flex;align-items:center;justify-content:center;color:var(--blue);flex-shrink:0">
              <UiAppIcon :name="t.transaction_type === 'credit' ? 'income' : 'expense'" :size="16" />
            </div>
            <div>
              <div style="font-size:13px;font-weight:500;color:var(--t1)">{{ t.description }}</div>
              <div style="font-size:11px;color:var(--t3);margin-top:1px">{{ t.transaction_type }}</div>
            </div>
            <div style="text-align:right">
              <div
                class="mono"
                :style="`font-size:13px;color:${t.transaction_type === 'credit' ? 'var(--ok)' : 'var(--t2)'}`"
              >
                {{ t.transaction_type === 'credit' ? '+' : '-' }} {{ formatBRL(parseFloat(t.amount)) }}
              </div>
              <div style="font-size:10px;color:var(--t4);margin-top:1px">{{ t.occurred_on }}</div>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })
const { open } = useModal()
const { transactions, isLoading, fetchTransactions } = useTransactions()
const { formatBRL } = useFormatters()

const now = new Date()
onMounted(() => fetchTransactions({ year: now.getFullYear(), month: now.getMonth() + 1 }))

const groupedTransactions = computed(() => {
  const groups: Record<string, typeof transactions.value> = {}
  for (const t of transactions.value) {
    if (!groups[t.occurred_on]) groups[t.occurred_on] = []
    groups[t.occurred_on].push(t)
  }
  return Object.entries(groups).sort(([a], [b]) => b.localeCompare(a))
})

function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' }).format(
    new Date(iso + 'T12:00:00')
  )
}
</script>
