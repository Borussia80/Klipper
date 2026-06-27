<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;display:flex;align-items:center;gap:12px;z-index:10">
      <div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Contas</div>
        <div style="font-size:11px;color:var(--t3)">{{ accounts.length }} contas</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
        <div style="text-align:right">
          <div style="font-size:10px;color:var(--t4)">Caixa disponível</div>
          <div class="mono" style="font-size:16px;font-weight:500;color:var(--t1);line-height:1.2">{{ formatBRL(totalBalance) }}</div>
        </div>
        <button class="btn btn-p" @click="open('nova-conta')">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          Nova conta
        </button>
      </div>
    </div>

    <div style="padding:20px 20px 32px">
      <!-- Skeleton while loading (wire-up point for real data fetch) -->
      <template v-if="isLoading">
        <UiSkeletonCard v-for="n in 5" :key="n" style="margin-bottom:8px" />
      </template>

      <template v-else>
        <template v-if="checkingAccounts.length">
          <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'JetBrains Mono',monospace;margin-bottom:10px">Contas correntes</div>
          <div v-for="acc in checkingAccounts" :key="acc.id" class="ac">
            <UiBankIcon :institution="acc.institution" :name="acc.name" :size="36" />
            <div style="flex:1;min-width:0">
              <div style="font-size:13px;font-weight:600;color:var(--t1)">{{ acc.name }}</div>
              <div style="font-size:11px;color:var(--t3)">{{ acc.institution }} · {{ acc.account_type }}</div>
            </div>
            <div style="text-align:right;flex-shrink:0">
              <div class="mono" style="font-size:15px;font-weight:500;color:var(--t1)">{{ formatBRL(parseFloat(acc.balance)) }}</div>
            </div>
          </div>
        </template>

        <template v-if="creditCards.length">
          <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'JetBrains Mono',monospace;margin:20px 0 10px">Cartões de crédito</div>
          <div v-for="acc in creditCards" :key="acc.id" class="ac">
            <UiBankIcon :institution="acc.institution" :name="acc.name" :size="36" />
            <div style="flex:1;min-width:0">
              <div style="font-size:13px;font-weight:600;color:var(--t1)">{{ acc.name }}</div>
              <div style="font-size:11px;color:var(--t3)">{{ acc.institution }}</div>
            </div>
            <div style="text-align:right;flex-shrink:0">
              <div class="mono" style="font-size:15px;font-weight:500;color:var(--warn)">{{ formatBRL(parseFloat(acc.balance)) }}</div>
            </div>
          </div>
        </template>

        <div v-if="!accounts.length" style="padding:48px 0;text-align:center;color:var(--t4);font-size:13px">
          Nenhuma conta cadastrada.
          <br />
          <button class="btn btn-p" style="margin-top:12px" @click="open('nova-conta')">Adicionar conta</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })
const { open } = useModal()
const { accounts, isLoading, fetchAccounts, totalBalance } = useAccounts()
const { formatBRL } = useFormatters()

onMounted(fetchAccounts)

const checkingAccounts = computed(() => accounts.value.filter((a) => a.account_type !== 'credit_card'))
const creditCards = computed(() => accounts.value.filter((a) => a.account_type === 'credit_card'))
</script>
