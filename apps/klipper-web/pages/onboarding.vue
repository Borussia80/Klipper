<template>
  <div
    style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);padding:24px"
  >
    <div style="width:min(520px, 100% - 48px)">

      <!-- Progress dots -->
      <div style="display:flex;justify-content:center;gap:8px;margin-bottom:32px">
        <div
          v-for="n in 3"
          :key="n"
          style="width:6px;height:6px;border-radius:50%;transition:background .2s"
          :style="{ background: currentStep === n ? 'var(--blue)' : 'var(--bd2)' }"
        />
      </div>

      <!-- Step card -->
      <div style="background:var(--sf);border:1px solid var(--bd2);border-radius:12px;padding:32px">

        <!-- Step label -->
        <div style="font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--t3);font-family:'JetBrains Mono',monospace;margin-bottom:20px">
          Passo {{ currentStep }} de 3
        </div>

        <!-- ═══ STEP 1 — Conectar banco ═══ -->
        <template v-if="currentStep === 1">
          <div style="font-size:22px;font-weight:300;letter-spacing:-.02em;color:var(--t1);margin-bottom:6px">Conecte sua conta bancária</div>
          <div style="font-size:13px;color:var(--t3);margin-bottom:24px">Klipper lê os dados, nunca movimenta</div>

          <!-- Bank grid -->
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px">
            <div
              v-for="bank in banks"
              :key="bank.id"
              tabindex="0"
              role="checkbox"
              :aria-checked="selectedBanks.includes(bank.id)"
              class="bank-card"
              :class="{ 'bank-card--selected': selectedBanks.includes(bank.id) }"
              @click="toggleBank(bank.id)"
              @keydown.enter.space.prevent="toggleBank(bank.id)"
            >
              <div
                class="bank-logo"
                :style="{ background: bank.bg, color: bank.fg, fontSize: bank.smallText ? '9px' : '14px', fontWeight: 700 }"
              >
                {{ bank.label }}
              </div>
              <div style="font-size:11px;color:var(--t2);margin-top:6px">{{ bank.name }}</div>
            </div>
          </div>

          <!-- Import OFX/CSV -->
          <button
            class="btn"
            style="width:100%;height:40px;background:transparent;border:1px solid var(--bd2);color:var(--t3);font-size:12px;margin-bottom:24px"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Importar extrato (OFX / CSV)
          </button>

          <!-- Actions -->
          <div style="display:flex;justify-content:space-between;align-items:center">
            <button
              class="btn"
              style="background:transparent;border:none;color:var(--t4);font-size:12px;padding:0"
              @click="next"
            >
              Pular por enquanto
            </button>
            <button class="btn btn-p" style="height:40px;padding:0 24px" @click="next">
              Continuar →
            </button>
          </div>
        </template>

        <!-- ═══ STEP 2 — Investimentos ═══ -->
        <template v-else-if="currentStep === 2">
          <div style="font-size:22px;font-weight:300;letter-spacing:-.02em;color:var(--t1);margin-bottom:6px">Seus investimentos</div>
          <div style="font-size:13px;color:var(--t3);margin-bottom:24px">Importamos seu extrato da B3</div>

          <!-- Drop zone -->
          <div
            class="drop-zone"
            :class="{ 'drop-zone--active': isDragOver }"
            style="border:2px dashed var(--bd2);border-radius:12px;padding:48px 24px;text-align:center;cursor:pointer;margin-bottom:20px;transition:border-color .15s, background .15s"
            @dragover.prevent="isDragOver = true"
            @dragleave="isDragOver = false"
            @drop.prevent="handleDrop"
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--t4);margin:0 auto 10px;display:block">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <div style="font-size:13px;color:var(--t2);margin-bottom:4px">Arraste o arquivo CEI / B3</div>
            <div style="font-size:12px;color:var(--t4)">ou clique para selecionar · CSV, OFX, XLS</div>
          </div>

          <!-- Alt actions -->
          <div style="display:flex;gap:10px;margin-bottom:24px">
            <button
              class="btn"
              style="flex:1;height:40px;background:transparent;border:1px solid var(--bd2);color:var(--t3);font-size:12px"
            >
              Conectar com corretora
            </button>
            <button
              class="btn"
              style="flex:1;height:40px;background:transparent;border:1px solid var(--bd2);color:var(--t3);font-size:12px"
            >
              Adicionar manualmente
            </button>
          </div>

          <!-- Actions -->
          <div style="display:flex;justify-content:space-between">
            <button class="btn" style="background:transparent;border:1px solid var(--bd2);color:var(--t3);height:40px" @click="prev">← Voltar</button>
            <button class="btn btn-p" style="height:40px;padding:0 24px" @click="next">Continuar →</button>
          </div>
        </template>

        <!-- ═══ STEP 3 — Metas ═══ -->
        <template v-else-if="currentStep === 3">
          <div style="font-size:22px;font-weight:300;letter-spacing:-.02em;color:var(--t1);margin-bottom:6px">Qual é sua prioridade agora?</div>
          <div style="font-size:13px;color:var(--t3);margin-bottom:24px">Você pode alterar isso depois a qualquer momento</div>

          <!-- Goal cards -->
          <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:24px">
            <div
              v-for="goal in goals"
              :key="goal.id"
              tabindex="0"
              role="radio"
              :aria-checked="selectedGoal === goal.id"
              class="goal-card"
              :class="{ 'goal-card--selected': selectedGoal === goal.id }"
              @click="selectedGoal = goal.id"
              @keydown.enter.space.prevent="selectedGoal = goal.id"
            >
              <div style="flex-shrink:0;color:var(--t2)"><UiAppIcon :name="goal.icon" :size="18" /></div>
              <span style="font-size:13px;color:var(--t1)">{{ goal.label }}</span>
            </div>
          </div>

          <!-- Monthly savings input -->
          <div style="margin-bottom:24px">
            <label style="display:block;font-size:11px;color:var(--t3);margin-bottom:8px;font-weight:500">Quanto quero guardar por mês</label>
            <div style="display:flex;align-items:center;gap:8px;background:var(--ly);border:1px solid var(--bd2);border-radius:var(--r);padding:0 12px;height:44px">
              <span style="font-size:13px;color:var(--t3);font-family:'JetBrains Mono',monospace">R$</span>
              <input
                v-model="savingsGoal"
                type="text"
                inputmode="numeric"
                placeholder="0,00"
                style="flex:1;background:transparent;border:none;outline:none;font-size:15px;color:var(--t1);font-family:'JetBrains Mono',monospace"
                aria-label="Meta de poupança mensal em reais"
              >
            </div>
          </div>

          <!-- Actions -->
          <div style="display:flex;justify-content:space-between">
            <button class="btn" style="background:transparent;border:1px solid var(--bd2);color:var(--t3);height:40px" @click="prev">← Voltar</button>
            <button class="btn btn-p" style="height:40px;padding:0 20px;font-size:12px" @click="finish">Começar a usar Klipper →</button>
          </div>
        </template>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const currentStep = ref(1)
const selectedBanks = ref<string[]>([])
const selectedGoal = ref<string | null>(null)
const savingsGoal = ref('')
const isDragOver = ref(false)

interface Bank {
  id: string
  name: string
  label: string
  bg: string
  fg: string
  smallText?: boolean
}

const banks: Bank[] = [
  { id: 'nubank',    name: 'Nubank',    label: 'N',   bg: 'var(--bank-nubank)', fg: '#fff' },
  { id: 'itau',      name: 'Itaú',      label: 'I',   bg: 'var(--bank-itau)',   fg: '#fff' },
  { id: 'btg',       name: 'BTG',       label: 'BTG', bg: 'var(--bank-btg)',    fg: '#4A9EFF', smallText: true },
  { id: 'bradesco',  name: 'Bradesco',  label: 'B',   bg: '#CC0000',            fg: '#fff' },
  { id: 'santander', name: 'Santander', label: 'S',   bg: '#EC0000',            fg: '#fff' },
  { id: 'c6',        name: 'C6 Bank',   label: 'C6',  bg: '#242424',            fg: '#F4C430' },
]

interface Goal {
  id: string
  icon: string
  label: string
}

const goals: Goal[] = [
  { id: 'casa',    icon: 'home',       label: 'Casa própria' },
  { id: 'aposent', icon: 'investment',  label: 'Aposentadoria' },
  { id: 'reserva', icon: 'target',      label: 'Reserva de emergência' },
]

function toggleBank(id: string) {
  const idx = selectedBanks.value.indexOf(id)
  if (idx === -1) {
    selectedBanks.value.push(id)
  } else {
    selectedBanks.value.splice(idx, 1)
  }
}

function handleDrop(_e: DragEvent) {
  isDragOver.value = false
  // File handling — requires backend integration
}

function next() {
  if (currentStep.value < 3) currentStep.value++
}

function prev() {
  if (currentStep.value > 1) currentStep.value--
}

async function finish() {
  await navigateTo('/dashboard')
}
</script>

<style scoped>
.bank-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 72px;
  border: 1px solid var(--bd2);
  border-radius: 8px;
  cursor: pointer;
  padding: 10px 6px;
  transition: border-color .15s, background .15s;
  user-select: none;
}
.bank-card:hover { border-color: rgba(43,125,244,0.35); }
.bank-card:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
.bank-card--selected { border-color: var(--blue); background: var(--bdm); }

.bank-logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: .02em;
}

.goal-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border: 1px solid var(--bd2);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color .15s, background .15s;
  user-select: none;
}
.goal-card:hover { border-color: rgba(43,125,244,0.35); }
.goal-card:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
.goal-card--selected { border-color: var(--blue); background: var(--bdm); }

.drop-zone:hover { border-color: var(--bd2); }
.drop-zone--active { border-color: var(--blue) !important; background: var(--bdm); }
</style>
