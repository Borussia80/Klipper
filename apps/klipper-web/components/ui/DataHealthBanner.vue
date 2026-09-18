<template>
  <div v-if="visivel" class="dh" data-testid="data-health">
    <div v-if="mostraCategoria" class="dh-item">
      <div class="dh-txt">
        <strong>{{ health!.uncategorized }} de {{ health!.transactions }}</strong> lançamentos ainda estão
        sem categoria. O orçamento e os relatórios por categoria ficam vazios até isso ser feito.
      </div>

      <div class="dh-track">
        <span class="dh-fill" data-testid="data-health-bar" :style="{ width: `${pct}%` }" />
      </div>

      <NuxtLink class="btn btn-p dh-cta" to="/transacoes">Categorizar lançamentos</NuxtLink>
    </div>

    <div v-if="mostraConta" class="dh-item" data-testid="sem-conta">
      <div class="dh-txt">
        <strong>{{ health!.without_account }}</strong> lançamentos não estão ligados a nenhuma conta.
        O saldo, o caixa e o patrimônio não fecham enquanto isso.
      </div>

      <div class="dh-acao">
        <div v-if="accounts.length" class="sel-wrap">
          <select
            v-model="contaEscolhida"
            class="fi fi-sel"
            data-testid="sem-conta-select"
            aria-label="Conta de destino dos lançamentos sem conta"
          >
            <option v-for="c in accounts" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
          </select>
          <span class="sel-caret" aria-hidden="true">▾</span>
        </div>

        <button
          class="btn btn-p dh-cta"
          type="button"
          data-testid="sem-conta-cta"
          :disabled="salvando"
          @click="corrigir"
        >
          {{ accounts.length ? 'Ligar à conta' : 'Cadastrar conta' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * A faixa que explica por que o resto da tela está vazio.
 *
 * São duas pendências da importação, e as duas produzem tela vazia por motivos
 * diferentes: sem categoria, orçamento e relatórios não têm o que mostrar; sem
 * conta, saldo e patrimônio não fecham. Ficam na mesma faixa porque é a mesma
 * pergunta do usuário — "por que não aparece nada?".
 */
import type { DataHealthReport } from '~/composables/useReports'

const props = defineProps<{ health: DataHealthReport | null }>()
const emit = defineEmits<{ corrigido: [] }>()

const { open } = useModal()
const { accounts, fetchAccounts } = useAccounts()
const { assignAccountToOrphans } = useTransactions()
const { addToast } = useToast()

// Metade: abaixo disso a categorização não é o que está travando as telas, e a
// faixa viraria um alerta permanente sobre a sobra que sempre existe.
const LIMITE = 0.5

const contaEscolhida = ref('')
const salvando = ref(false)

const pct = computed(() => {
  if (!props.health?.transactions) return 0
  return Math.round((props.health.uncategorized / props.health.transactions) * 100)
})

const mostraCategoria = computed(() => {
  const h = props.health
  if (!h || h.transactions === 0 || h.uncategorized === 0) return false
  return h.uncategorized / h.transactions >= LIMITE
})

const mostraConta = computed(() => (props.health?.without_account ?? 0) > 0)

const visivel = computed(() => mostraCategoria.value || mostraConta.value)

// Sem conta cadastrada não há o que escolher: mandar escolher seria um beco sem
// saída, e é exatamente o estado de quem importou o extrato antes do UR-2.
async function corrigir() {
  if (!accounts.value.length) {
    open('nova-conta')
    return
  }

  const id = Number(contaEscolhida.value || accounts.value[0]!.id)
  salvando.value = true
  try {
    const updated = await assignAccountToOrphans(id)
    addToast(`${updated} lançamentos ligados à conta`, 'ok')
    emit('corrigido')
  } catch {
    addToast('Não foi possível ligar os lançamentos. Tente novamente.', 'alert')
  } finally {
    salvando.value = false
  }
}

onMounted(() => {
  if (!accounts.value.length) fetchAccounts()
})
</script>

<style scoped>
.dh {
  background: var(--wnd); border: 1px solid var(--warn); border-radius: var(--r);
  padding: 14px 16px; display: grid; gap: 16px;
}
.dh-item { display: grid; gap: 10px; }
.dh-item + .dh-item { border-top: 1px solid var(--warn); padding-top: 16px; }

.dh-txt { font-size: 13px; color: var(--t2); line-height: 1.5; }
.dh-txt strong { color: var(--warn); font-weight: 600; }

.dh-track { height: 5px; background: var(--sf); border-radius: 3px; overflow: hidden; }
.dh-fill { display: block; height: 100%; background: var(--warn); }

.dh-acao { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.dh-cta { justify-self: start; height: 34px; font-size: 12px; }

.sel-wrap { position: relative; }
.fi-sel {
  -webkit-appearance: none; appearance: none; cursor: pointer;
  padding-right: 32px; height: 34px; font-size: 12px; margin: 0;
}
.sel-caret {
  position: absolute; right: 11px; top: 50%; transform: translateY(-50%);
  color: var(--t3); font-size: 11px; pointer-events: none; line-height: 1;
}
</style>
