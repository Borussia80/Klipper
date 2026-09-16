<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;display:flex;align-items:center;gap:12px;z-index:10">
      <div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Transações</div>
        <div style="font-size:11px;color:var(--t3)">{{ fmtMonthFull() }} · {{ filteredTransactions.length }} lançamento{{ filteredTransactions.length !== 1 ? 's' : '' }}</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:6px;min-width:0">
        <div class="filter-pills">
          <button :class="['pill', activeFilter === 'all' ? 'on' : '']" @click="activeFilter = 'all'">Todos</button>
          <button :class="['pill', activeFilter === 'credit' ? 'on' : '']" @click="activeFilter = 'credit'">Entradas</button>
          <button :class="['pill', activeFilter === 'debit' ? 'on' : '']" @click="activeFilter = 'debit'">Saídas</button>
        </div>
        
        <div style="width:1px;height:16px;background:var(--bd2);margin:0 2px;flex-shrink:0"></div>

        <!-- View mode toggle (Compact vs Comfortable) -->
        <button
          type="button"
          class="btn-i"
          :title="isCompactView ? 'Mudar para visualização confortável' : 'Mudar para visualização compacta'"
          :aria-label="isCompactView ? 'Visualização confortável' : 'Visualização compacta'"
          @click="isCompactView = !isCompactView"
        >
          <UiAppIcon :name="isCompactView ? 'grid' : 'rows'" :size="15" />
        </button>

        <button class="btn btn-g" @click="open('novo-lancamento')">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          Adicionar
        </button>
      </div>
    </div>

    <!-- Bulk Actions Toolbar -->
    <div
      v-if="selectedIds.length > 0"
      class="bulk-toolbar"
    >
      <div style="display:flex;align-items:center;gap:10px">
        <span class="bulk-count">{{ selectedIds.length }} selecionada{{ selectedIds.length !== 1 ? 's' : '' }}</span>
        <button class="bulk-link" type="button" @click="selectAll">Selecionar todas ({{ filteredTransactions.length }})</button>
        <button class="bulk-link" type="button" @click="clearSelection">Limpar</button>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <button class="btn btn-g" style="color:var(--alert);border-color:rgba(232,115,90,0.4)" type="button" @click="confirmDeleteBulk">
          <UiAppIcon name="trash" :size="13" />
          Excluir selecionadas
        </button>
      </div>
    </div>

    <div style="padding:0 20px 32px">
      <!-- Skeleton while loading -->
      <UiSkeletonTransactionList v-if="isLoading" :count="4" />

      <template v-else>
        <div v-if="!filteredTransactions.length" style="padding:60px 0;text-align:center;color:var(--t3);font-size:13px">
          Nenhum lançamento no período.
          <div style="margin-top:14px;display:flex;justify-content:center;gap:8px">
            <button class="btn btn-p" @click="open('novo-lancamento')">Adicionar lançamento</button>
            <NuxtLink to="/importar" class="btn btn-g">Importar extrato</NuxtLink>
          </div>
        </div>

        <template v-for="[date, txns] in groupedTransactions" :key="date">
          <div class="gh">
            <span class="gl">{{ formatDayMonth(date) }}</span>
            <span class="gr"></span>
            <span class="gc">{{ txns.length }} lançamento{{ txns.length !== 1 ? 's' : '' }}</span>
          </div>

          <!-- Transaction rows (Supports standard and compact density + multi-selection) -->
          <div
            v-for="t in txns"
            :key="t.id"
            class="txr"
            :class="{ 'is-compact': isCompactView, 'is-selected': selectedIds.includes(t.id) }"
            @click="open('editar-lancamento', t)"
          >
            <!-- Checkbox for bulk select -->
            <div class="tx-check" @click.stop="toggleSelect(t.id)">
              <input
                type="checkbox"
                :checked="selectedIds.includes(t.id)"
                :aria-label="`Selecionar transação ${t.description}`"
                class="tx-checkbox"
                @click.stop="toggleSelect(t.id)"
              />
            </div>

            <div class="tx-icon" style="border-radius:9px;background:rgba(43,125,244,0.1);display:flex;align-items:center;justify-content:center;color:var(--blue);flex-shrink:0">
              <UiAppIcon :name="t.transaction_type === 'credit' ? 'income' : 'expense'" :size="isCompactView ? 14 : 16" />
            </div>
            <div style="min-width:0">
              <div style="font-size:13px;font-weight:500;color:var(--t1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ t.description }}</div>
              <div v-if="!isCompactView" style="font-size:11px;color:var(--t3);margin-top:1px">{{ t.transaction_type }}</div>
            </div>
            <div style="text-align:right;white-space:nowrap">
              <div
                class="mono"
                :style="`font-size:13px;color:${t.transaction_type === 'credit' ? 'var(--ok)' : 'var(--t2)'}`"
              >
                {{ t.transaction_type === 'credit' ? '+' : '-' }} {{ formatBRL(parseFloat(t.amount)) }}
              </div>
              <div v-if="!isCompactView" style="font-size:10px;color:var(--t3);margin-top:1px">{{ formatDayMonth(t.occurred_on) }}</div>
            </div>
            <button
              type="button"
              class="tx-delete"
              :aria-label="`Excluir lançamento ${t.description}`"
              title="Excluir lançamento"
              @click.stop="confirmDeleteTransaction(t)"
            >
              <UiAppIcon name="trash" :size="14" />
            </button>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Transaction } from '~/composables/useTransactions'

definePageMeta({ layout: 'app' })
const { open } = useModal()
const { transactions, isLoading, fetchTransactions, deleteTransaction } = useTransactions()
const { formatBRL, fmtMonthFull, formatDayMonth } = useFormatters()
const { addToast } = useToast()

const now = new Date()
onMounted(() => fetchTransactions({ year: now.getFullYear(), month: now.getMonth() + 1 }))

const activeFilter = ref<'all' | 'credit' | 'debit'>('all')
const isCompactView = ref(false)
const selectedIds = ref<number[]>([])

// A seleção não sobrevive à troca de filtro — linhas que somem da tela não
// podem continuar marcadas para uma exclusão em lote que o usuário não vê mais.
watch(activeFilter, () => {
  selectedIds.value = []
})

const filteredTransactions = computed(() =>
  activeFilter.value === 'all'
    ? transactions.value
    : transactions.value.filter((t) => t.transaction_type === activeFilter.value)
)

const groupedTransactions = computed(() => {
  const groups: Record<string, typeof transactions.value> = {}
  for (const t of filteredTransactions.value) {
    if (!groups[t.occurred_on]) groups[t.occurred_on] = []
    groups[t.occurred_on].push(t)
  }
  return Object.entries(groups).sort(([a], [b]) => b.localeCompare(a))
})

function toggleSelect(id: number) {
  selectedIds.value = selectedIds.value.includes(id)
    ? selectedIds.value.filter((i: number) => i !== id)
    : [...selectedIds.value, id]
}

function selectAll() {
  selectedIds.value = filteredTransactions.value.map((t: Transaction) => t.id)
}

function clearSelection() {
  selectedIds.value = []
}

function confirmDeleteTransaction(t: typeof transactions.value[number]) {
  open('confirm-delete', {
    title: 'Excluir lançamento',
    resourceType: 'lançamento',
    itemName: `${t.description} · ${formatBRL(parseFloat(t.amount))}`,
    description: 'O lançamento será removido do período atual e os totais serão recalculados.',
    onConfirm: () => deleteTransaction(t.id),
  })
}

async function deleteBulkSelected() {
  const ids = [...selectedIds.value]
  const results = await Promise.allSettled(ids.map((id) => deleteTransaction(id, { silent: true })))
  const failedIds = ids.filter((_, i) => results[i].status === 'rejected')
  const succeededCount = ids.length - failedIds.length

  // Mantém selecionados só os que falharam — dá pra tentar excluir de novo
  // sem reincluir os que já foram removidos com sucesso.
  selectedIds.value = failedIds

  if (succeededCount > 0) {
    addToast(`${succeededCount} lançamento${succeededCount !== 1 ? 's' : ''} removido${succeededCount !== 1 ? 's' : ''}`, 'ok')
  }
  if (failedIds.length > 0) {
    addToast(`Não foi possível excluir ${failedIds.length} lançamento${failedIds.length !== 1 ? 's' : ''}.`, 'alert')
  }
}

function confirmDeleteBulk() {
  const count = selectedIds.value.length
  open('confirm-delete', {
    title: `Excluir ${count} lançamentos`,
    resourceType: 'lançamentos selecionados',
    itemName: `${count} transações em lote`,
    description: 'Todas as transações selecionadas serão excluídas permanentemente.',
    onConfirm: deleteBulkSelected,
  })
}
</script>

<style scoped>
.filter-pills {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x proximity;
  -webkit-mask-image: linear-gradient(to right, transparent, black 12px, black calc(100% - 12px), transparent);
  mask-image: linear-gradient(to right, transparent, black 12px, black calc(100% - 12px), transparent);
}

.filter-pills::-webkit-scrollbar {
  display: none;
}

.filter-pills .pill {
  flex-shrink: 0;
  scroll-snap-align: start;
}

.tx-delete {
  width: 30px;
  height: 30px;
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--t3);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.12s, color 0.12s, border-color 0.12s, background 0.12s;
}

.bulk-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
  background: var(--bdm);
  border-bottom: 1px solid rgba(91, 155, 213, 0.28);
  font-size: 12.5px;
}

.bulk-count {
  font-weight: 600;
  color: var(--blt);
}

.bulk-link {
  background: none;
  border: none;
  color: var(--blue);
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
  padding: 0 4px;
}

.txr {
  grid-template-columns: 24px 36px 1fr auto 30px;
  transition: background 0.1s, padding 0.1s;
}

.txr.is-selected {
  background: rgba(91, 155, 213, 0.08);
}

.txr.is-compact {
  padding: 5px 8px;
  grid-template-columns: 20px 28px 1fr auto 26px;
  gap: 8px;
}

.txr.is-compact .tx-icon {
  width: 28px !important;
  height: 28px !important;
  border-radius: 6px !important;
}

.tx-check {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tx-checkbox {
  cursor: pointer;
  accent-color: var(--blue);
  width: 14px;
  height: 14px;
}

.txr:hover .tx-delete,
.tx-delete:focus-visible {
  opacity: 1;
}

.tx-delete:hover {
  color: var(--alert);
  border-color: rgba(232, 115, 90, 0.32);
  background: var(--ald);
}

@media (hover: none) {
  .tx-delete {
    opacity: 1;
  }
}
</style>
