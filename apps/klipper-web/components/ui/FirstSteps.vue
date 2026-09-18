<script setup lang="ts">
/**
 * UR-4 — Primeiros passos do painel. Substitui `pages/onboarding.vue`, que
 * funcionava mas não tinha rota chegando nela e prometia conexão bancária e
 * importação da B3 que o app não faz.
 *
 * Cada etapa é marcada a partir do dado que já existe no sistema. Nada aqui
 * guarda "etapa concluída" por conta própria: o que fica lembrado é só a
 * escolha de ocultar o bloco.
 */
import type { ModalName } from '~/composables/useModal'

interface Etapa {
  label: string
  cta: string
  modal: ModalName
  payload?: string
  done: boolean
}

const { open } = useModal()
const { accounts, fetchAccounts } = useAccounts()
const { investments, fetchInvestments } = useInvestments()
const { budgets, fetchBudgets } = useBudgets()

const oculto = useCookie<boolean | null>('klipper_primeiros_passos_oculto', {
  sameSite: 'lax',
  maxAge: 60 * 60 * 24 * 365,
})
const carregado = ref(false)

const etapas = computed<Etapa[]>(() => [
  {
    label: 'Cadastrar a primeira conta',
    cta: 'Cadastrar conta',
    modal: 'nova-conta',
    done: accounts.value.some((c) => c.account_type !== 'credit_card'),
  },
  {
    label: 'Cadastrar os cartões de crédito',
    cta: 'Cadastrar cartão',
    modal: 'nova-conta',
    payload: 'cartao',
    done: accounts.value.some((c) => c.account_type === 'credit_card'),
  },
  {
    label: 'Registrar a carteira de investimentos',
    cta: 'Registrar aporte',
    modal: 'novo-aporte',
    done: investments.value.length > 0,
  },
  {
    label: 'Definir o primeiro objetivo financeiro',
    cta: 'Definir objetivo',
    modal: 'nova-categoria',
    done: budgets.value.length > 0,
  },
])

const concluidas = computed(() => etapas.value.filter((e: Etapa) => e.done).length)
const pct = computed(() => Math.round((concluidas.value / etapas.value.length) * 100))

// Só aparece depois que os três fetches voltaram: marcar etapa como pendente
// antes de saber se ela existe é inventar estado.
const visivel = computed(() => carregado.value && !oculto.value && concluidas.value < etapas.value.length)

onMounted(async () => {
  if (oculto.value) return
  await Promise.all([fetchAccounts(), fetchInvestments(), fetchBudgets()])
  carregado.value = true
})
</script>

<template>
  <section v-if="visivel" class="fs" aria-labelledby="fs-title">
    <div class="fs-head">
      <div>
        <div id="fs-title" class="fs-title">Primeiros passos</div>
        <div class="fs-sub">{{ concluidas }} de {{ etapas.length }} concluídos · {{ pct }}%</div>
      </div>
      <button class="fs-hide" type="button" @click="oculto = true">Ocultar</button>
    </div>

    <div
      class="fs-track"
      role="progressbar"
      aria-label="Progresso dos primeiros passos"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-valuenow="pct"
    >
      <span class="fs-fill" :style="{ width: pct + '%' }"></span>
    </div>

    <ul class="fs-list">
      <li v-for="etapa in etapas" :key="etapa.label" class="fs-item" :class="{ done: etapa.done }">
        <span class="fs-mark" aria-hidden="true">{{ etapa.done ? '✓' : '' }}</span>
        <span class="fs-label">{{ etapa.label }}</span>
        <button
          v-if="!etapa.done"
          class="btn btn-g fs-cta"
          type="button"
          @click="open(etapa.modal, etapa.payload ?? null)"
        >
          {{ etapa.cta }}
        </button>
        <span v-else class="fs-done">Concluído</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.fs {
  background: var(--sf); border: 1px solid var(--bd); border-radius: var(--r);
  padding: 17px 18px;
}
.fs-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.fs-title { font-family: 'Space Grotesk'; font-size: 15px; font-weight: 600; }
.fs-sub { color: var(--t3); font-size: 12.5px; margin-top: 3px; }
.fs-hide {
  background: none; border: none; color: var(--t3); font-size: 12px;
  cursor: pointer; padding: 2px 4px; flex: none;
}
.fs-hide:hover { color: var(--t2); }

.fs-track { height: 7px; background: var(--bg); border-radius: 4px; overflow: hidden; margin: 14px 0 4px; }
.fs-fill { display: block; height: 100%; border-radius: 4px; background: var(--sea); transition: width .2s; }

.fs-list { list-style: none; margin: 0; padding: 0; }
.fs-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 0; border-bottom: 1px solid var(--bd);
}
.fs-item:last-child { border-bottom: none; padding-bottom: 0; }
.fs-mark {
  width: 18px; height: 18px; border-radius: 50%; flex: none;
  border: 1px solid var(--bd2); display: grid; place-items: center;
  font-size: 11px; color: var(--ok);
}
.fs-item.done .fs-mark { border-color: var(--ok); }
.fs-label { flex: 1; min-width: 0; font-size: 13px; color: var(--t2); }
.fs-item.done .fs-label { color: var(--t3); text-decoration: line-through; }
.fs-cta { flex: none; font-size: 12.5px; padding: 6px 12px; }
.fs-done { flex: none; font-size: 12px; color: var(--ok); }

@media (max-width: 480px) {
  .fs-item { flex-wrap: wrap; }
  .fs-cta, .fs-done { margin-left: 30px; }
}
</style>
