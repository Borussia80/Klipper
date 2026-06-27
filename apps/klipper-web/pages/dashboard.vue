<template>
  <div>
    <!-- Cockpit hero -->
    <div style="padding:32px 24px 0">
      <div class="mono" style="font-size:10px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--t4);margin-bottom:28px">Jun 2026 · 22 · Segunda</div>

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
        <div style="font-size:12px;color:var(--t3);line-height:1.55">Taxa de poupança de 28,9% em junho — 3,1 pontos acima de maio. Continue assim.</div>
      </div>
    </div>

    <!-- Alertas -->
    <div style="padding:0 20px;margin-top:24px">
      <div style="font-size:10px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--t4);font-family:'JetBrains Mono',monospace;margin-bottom:10px">Atenção necessária</div>

      <div style="border-left:3px solid var(--alert);padding:13px 16px;border-radius:0 8px 8px 0;background:rgba(232,53,53,0.04);margin-bottom:8px">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:16px">
          <div>
            <div style="font-size:13px;font-weight:500;color:var(--t1)">Conta de Luz vence em 3 dias</div>
            <div style="font-size:11px;color:var(--t3);margin-top:2px">CPFL Energia · 25 Jun · não paga</div>
          </div>
          <div style="text-align:right;flex-shrink:0">
            <div class="mono" style="font-size:13px;font-weight:500;color:var(--alert)">R$ 420,00</div>
            <div style="font-size:10px;color:var(--blue);cursor:pointer;margin-top:3px">registrar →</div>
          </div>
        </div>
      </div>

      <div style="border-left:3px solid var(--warn);padding:13px 16px;border-radius:0 8px 8px 0;background:rgba(229,144,16,0.04)">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:16px">
          <div>
            <div style="font-size:13px;font-weight:500;color:var(--t1)">Restaurantes em 87% do orçamento</div>
            <div style="font-size:11px;color:var(--t3);margin-top:2px">R$ 156 livres · 8 dias restantes no mês</div>
          </div>
          <div style="text-align:right;flex-shrink:0">
            <NuxtLink to="/orcamento" style="font-size:10px;color:var(--blue);cursor:pointer">ver orçamento →</NuxtLink>
          </div>
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

const { accounts, totalBalance, isLoading, fetchAccounts } = useAccounts()
const { transactions, totalDebits, totalCredits, fetchTransactions } = useTransactions()
const { formatBRL } = useFormatters()

const now = new Date()
onMounted(() => {
  fetchAccounts()
  fetchTransactions({ year: now.getFullYear(), month: now.getMonth() + 1 })
})

const recentTransactions = computed(() => transactions.value.slice(0, 5))

function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' }).format(
    new Date(iso + 'T12:00:00')
  )
}
</script>
