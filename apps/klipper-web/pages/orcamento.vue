<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;display:flex;align-items:center;gap:12px;z-index:10">
      <div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Orçamento</div>
        <div style="font-size:11px;color:var(--t3)">{{ fmtMonthFull() }} · {{ daysLeftInMonth() }} dias restantes</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:6px">
        <button class="sel-chip">
          Junho 2026
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2.5 4L5 6.5 7.5 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <button class="btn btn-g" @click="open('nova-categoria')">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          Nova categoria
        </button>
      </div>
    </div>

    <div style="padding:0 20px 32px">
      <!-- Summary tiles -->
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0">
        <div style="background:var(--sf);border:1px solid var(--bd2);border-radius:8px;padding:12px">
          <div class="plbl" style="margin-bottom:4px">Alocado</div>
          <div class="mono" style="font-size:18px;font-weight:500;color:var(--t1)">{{ formatBRL(totalAllocated) }}</div>
        </div>
        <div style="background:var(--sf);border:1px solid var(--bd2);border-radius:8px;padding:12px">
          <div class="plbl" style="margin-bottom:4px">Gasto</div>
          <div class="mono" style="font-size:18px;font-weight:500;color:var(--warn)">{{ formatBRL(totalSpent) }}</div>
        </div>
        <div style="background:var(--sf);border:1px solid var(--bd2);border-radius:8px;padding:12px">
          <div class="plbl" style="margin-bottom:4px">Livre</div>
          <div class="mono" style="font-size:18px;font-weight:500;color:var(--ok)">{{ formatBRL(totalFree) }}</div>
        </div>
      </div>

      <UiSkeletonCard v-if="isLoading" v-for="n in 4" :key="n" style="margin-bottom:8px" />
      <template v-else>
        <UiBudgetCategoryCard v-for="cat in categories" :key="cat.name" v-bind="cat" />
        <div v-if="!categories.length" style="padding:40px 0;text-align:center;color:var(--t4);font-size:13px">
          Nenhum orçamento para o período.
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })
const { open } = useModal()
const { summary, isLoading, fetchSummary } = useBudgets()
const { formatBRL, fmtMonthFull, daysLeftInMonth } = useFormatters()

const now = new Date()

onMounted(() => fetchSummary(now.getFullYear(), now.getMonth() + 1))

const categories = computed(() =>
  summary.value.map((row) => ({
    icon: row.category_icon,
    name: row.category_name,
    pct: Math.round(row.pct_used),
    spent: row.spent,
    limit: row.amount_limit,
    daysLeft: daysLeftInMonth(),
  }))
)

const totalAllocated = computed(() => summary.value.reduce((s, r) => s + Number(r.amount_limit), 0))
const totalSpent = computed(() => summary.value.reduce((s, r) => s + Number(r.spent), 0))
const totalFree = computed(() => totalAllocated.value - totalSpent.value)
</script>
