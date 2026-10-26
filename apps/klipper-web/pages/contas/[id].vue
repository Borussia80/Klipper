<template>
  <div style="padding:20px;max-width:760px">
    <NuxtLink to="/contas" class="back-link">← Contas</NuxtLink>
    <div v-if="error" role="alert" class="error">{{ error }}</div>
    <template v-else-if="history">
      <p class="eyebrow">Histórico de saldo</p>
      <h1>{{ accountName }}</h1>
      <div class="balance-card">
        <span>Saldo realizado</span>
        <strong class="mono">{{ formatBRL(Number(history.closing_balance)) }}</strong>
        <small>Saldo inicial: {{ formatBRL(Number(history.opening_balance)) }}</small>
      </div>
      <div v-if="!history.entries.length" class="empty">Ainda não há movimentos efetivados nesta conta.</div>
      <ol v-else class="history-list">
        <li v-for="entry in history.entries" :key="entry.id">
          <span>{{ entry.description }} · {{ entry.occurred_on }}</span>
          <span class="mono" :class="Number(entry.delta) >= 0 ? 'income' : 'expense'">
            {{ Number(entry.delta) >= 0 ? '+' : '−' }} {{ formatBRL(Math.abs(Number(entry.delta))) }}
          </span>
          <strong class="mono">{{ formatBRL(Number(entry.balance)) }}</strong>
        </li>
      </ol>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { BalanceHistory } from '~/composables/useAccounts'

definePageMeta({ layout: 'app' })
const route = useRoute()
const { accounts, fetchAccounts, fetchBalanceHistory } = useAccounts()
const { formatBRL } = useFormatters()
const history = ref<BalanceHistory | null>(null)
const error = ref<string | null>(null)
const id = Number(route.params.id)
const accountName = computed(() => accounts.value.find((account) => account.id === id)?.name ?? 'Conta')

onMounted(async () => {
  try {
    await fetchAccounts()
    history.value = await fetchBalanceHistory(id)
  } catch {
    error.value = 'Não foi possível carregar o histórico de saldo. Tente novamente.'
  }
})
</script>

<style scoped>
.back-link { color: var(--blue); font-size: 13px; text-decoration: none; }
h1 { color: var(--t1); font-size: 24px; margin: 4px 0 18px; }
.eyebrow { color: var(--t3); font-size: 11px; margin: 18px 0 0; text-transform: uppercase; letter-spacing: .08em; }
.balance-card { background: var(--sf); border: 1px solid var(--bd2); border-radius: var(--r); display: grid; gap: 6px; padding: 18px; }
.balance-card span, .balance-card small { color: var(--t3); font-size: 12px; }
.balance-card strong { color: var(--t1); font-size: 24px; }
.history-list { list-style: none; margin: 16px 0; padding: 0; }
.history-list li { display: grid; grid-template-columns: 1fr auto auto; gap: 14px; align-items: center; border-bottom: 1px solid var(--bd); color: var(--t2); font-size: 13px; padding: 12px 0; }
.income { color: var(--ok); }.expense { color: var(--alert); }.empty, .error { color: var(--t3); padding: 18px 0; }.error { color: var(--alert); }
@media (max-width: 420px) { .history-list li { grid-template-columns: 1fr auto; }.history-list li strong { grid-column: 2; } }
</style>
