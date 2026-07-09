<template>
  <div>
    <!-- Header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;z-index:10">
      <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Importar Extrato</div>
      <div style="font-size:11px;color:var(--t3)">Formatos suportados: CSV, extrato Itaú (PDF), fatura Itaú (PDF)</div>
    </div>

    <div style="padding:24px 20px 40px;max-width:560px">

      <!-- PDF PREVIEW STATE -->
      <template v-if="preview">
        <div style="background:var(--sf);border:1px solid var(--bd2);border-radius:8px;padding:12px 14px;margin-bottom:16px">
          <div style="font-size:11px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px">Layout detectado</div>
          <div style="font-size:13px;color:var(--t1)">{{ adapterLabel(preview.adapter) }}</div>
        </div>

        <div v-if="preview.warnings.length" role="alert" style="background:var(--ald);border:1px solid var(--alert);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px">
          <div style="font-weight:600;margin-bottom:4px">{{ preview.warnings.length }} linha{{ preview.warnings.length !== 1 ? 's' : '' }} não reconhecida{{ preview.warnings.length !== 1 ? 's' : '' }}</div>
          <div v-for="(w, i) in preview.warnings" :key="i">Página {{ w.page }}: {{ w.reason }}</div>
        </div>

        <div style="font-size:11px;color:var(--t3);margin-bottom:8px">
          {{ checkedRows.length }} de {{ preview.rows.length }} lançamentos selecionados
        </div>

        <div style="max-height:400px;overflow-y:auto;border:1px solid var(--bd2);border-radius:8px;margin-bottom:20px">
          <template v-for="group in groupedRows" :key="group.cardholder ?? '__none__'">
            <div
              v-if="group.cardholder"
              style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:var(--sf);border-bottom:1px solid var(--bd2)"
            >
              <div style="flex:1;min-width:0;font-size:11px;color:var(--t3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ group.cardholder }}</div>
              <div class="sel-wrap">
                <select
                  :value="selectedMemberByGroup[group.cardholder] ?? ''"
                  class="fi fi-sel"
                  aria-label="Portador do cartão"
                  @change="onGroupMemberChange(group.cardholder, $event)"
                >
                  <option value="">Nenhum</option>
                  <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
                </select>
                <span class="sel-caret" aria-hidden="true">▾</span>
              </div>
            </div>
            <label
              v-for="(row, i) in group.rows"
              :key="i"
              style="display:flex;align-items:center;gap:10px;padding:10px 12px;border-bottom:1px solid var(--bd2);cursor:pointer"
            >
              <input v-model="checkedRows" type="checkbox" :value="row" />
              <div style="flex:1;min-width:0">
                <div style="font-size:12px;color:var(--t1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ row.description }}</div>
                <div style="font-size:11px;color:var(--t4)">{{ formatRowDate(row.occurred_on) }}<template v-if="row.installment_number"> · parcela {{ row.installment_number }}/{{ row.installment_total }}</template></div>
              </div>
              <div style="font-size:12px;font-family:var(--mono);color:var(--t2);white-space:nowrap">{{ formatRowAmount(row.amount) }}</div>
            </label>
          </template>
        </div>

        <!-- Error banner -->
        <div v-if="error" role="alert" style="background:var(--ald);border:1px solid var(--alert);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px">
          {{ error }}
        </div>

        <div style="display:flex;gap:10px">
          <button class="btn btn-g" style="flex:1" @click="handleReset">Cancelar</button>
          <button
            class="btn btn-p"
            style="flex:2"
            :disabled="!checkedRows.length || isLoading"
            @click="handleConfirm"
          >
            <span v-if="isLoading" class="btn-spinner" aria-hidden="true" />
            {{ isLoading ? 'Confirmando…' : 'Confirmar importação' }}
          </button>
        </div>
      </template>

      <!-- IDLE / UPLOAD STATE -->
      <template v-else-if="!result">
        <!-- Drop zone -->
        <div
          class="drop-zone"
          :class="{ dragging: isDragging, 'has-file': !!selectedFile }"
          role="button"
          tabindex="0"
          aria-label="Área de upload de extrato CSV ou PDF"
          @click="triggerFileInput"
          @keydown.enter.space.prevent="triggerFileInput"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
        >
          <svg v-if="!selectedFile" width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 3v10M9 6l3-3 3 3M5 19a2 2 0 01-2-2v-4a2 2 0 012-2h3M16 11h3a2 2 0 012 2v4a2 2 0 01-2 2H5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true" style="color:var(--ok)">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M14 2v6h6M9 15l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>

          <div v-if="!selectedFile" style="text-align:center">
            <div style="font-size:13px;font-weight:500;color:var(--t1);margin-bottom:4px">
              {{ isDragging ? 'Solte o arquivo aqui' : 'Clique ou arraste o arquivo CSV ou PDF' }}
            </div>
            <div style="font-size:11px;color:var(--t4)">Máx. 5 MB · .csv, .pdf (extrato/fatura Itaú)</div>
          </div>
          <div v-else style="text-align:center">
            <div style="font-size:13px;font-weight:500;color:var(--t1);margin-bottom:2px">{{ selectedFile.name }}</div>
            <div style="font-size:11px;color:var(--t4)">{{ formatBytes(selectedFile.size) }}</div>
          </div>
        </div>

        <input
          ref="fileInputRef"
          type="file"
          accept=".csv,.pdf,text/csv,application/pdf"
          style="display:none"
          aria-hidden="true"
          @change="onFileChange"
        />

        <!-- Account selector -->
        <div style="margin:16px 0">
          <label class="plbl" for="import-account" style="display:block;margin-bottom:6px">
            Conta de destino <span style="color:var(--t4)">(opcional)</span>
          </label>
          <div class="sel-wrap">
            <select id="import-account" v-model="selectedAccountId" class="fi fi-sel" aria-label="Conta para creditar as transações">
              <option :value="undefined">Sem conta vinculada</option>
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
            </select>
            <span class="sel-caret" aria-hidden="true">▾</span>
          </div>
        </div>

        <!-- Error banner -->
        <div v-if="error" role="alert" style="background:var(--ald);border:1px solid var(--alert);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px">
          {{ error }}
        </div>

        <!-- Format hint -->
        <div style="background:var(--sf);border:1px solid var(--bd2);border-radius:8px;padding:12px 14px;margin-bottom:20px">
          <div style="font-size:11px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px">Formato esperado do CSV</div>
          <code style="font-size:11px;color:var(--t2);font-family:var(--mono);line-height:1.6;display:block;white-space:pre">Data,Descrição,Valor
01/06/2026,SUPERMERCADO EXTRA,-150.00
05/06/2026,PIX RECEBIDO SALÁRIO,5000.00
10/06/2026,POSTO SHELL,-120.50</code>
          <div style="font-size:11px;color:var(--t4);margin-top:8px">PDFs de extrato ou fatura Itaú têm o layout detectado automaticamente — você revisa os lançamentos antes de confirmar.</div>
        </div>

        <button
          class="btn btn-p"
          style="width:100%"
          :disabled="!selectedFile || isLoading"
          @click="handleUpload"
        >
          <span v-if="isLoading" class="btn-spinner" aria-hidden="true" />
          {{ isLoading ? 'Processando…' : isPdfSelected ? 'Analisar arquivo' : 'Importar transações' }}
        </button>
      </template>

      <!-- RESULT STATE -->
      <template v-else>
        <!-- Success card -->
        <div class="result-card" :class="result.errors.length ? 'has-errors' : 'all-ok'">
          <div style="font-size:28px;font-weight:700;color:var(--t1)">{{ result.imported }}</div>
          <div style="font-size:13px;color:var(--t3);margin-top:2px">
            transaç{{ result.imported === 1 ? 'ão importada' : 'ões importadas' }}
          </div>
          <div v-if="result.duplicates" style="font-size:12px;color:var(--t3);margin-top:6px">
            {{ result.duplicates }} duplicata{{ result.duplicates !== 1 ? 's' : '' }} ignorada{{ result.duplicates !== 1 ? 's' : '' }} (já importada{{ result.duplicates !== 1 ? 's' : '' }} anteriormente)
          </div>
        </div>

        <!-- Errors list -->
        <div v-if="result.errors.length" style="margin:16px 0">
          <div style="font-size:11px;font-weight:600;color:var(--alert);text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">
            {{ result.errors.length }} linha{{ result.errors.length !== 1 ? 's' : '' }} ignorada{{ result.errors.length !== 1 ? 's' : '' }}
          </div>
          <div
            v-for="(err, i) in result.errors"
            :key="i"
            style="font-size:12px;color:var(--t3);padding:6px 10px;background:var(--sf);border-radius:6px;margin-bottom:4px;font-family:var(--mono)"
          >{{ err }}</div>
        </div>

        <div style="display:flex;gap:10px;margin-top:20px">
          <button class="btn btn-g" style="flex:1" @click="goToTransactions">Ver transações</button>
          <button class="btn btn-g" style="flex:1" @click="handleReset">Importar outro</button>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })

const router = useRouter()
const { accounts, fetchAccounts } = useAccounts()
const { members, fetchMembers } = useMembers()
const { result, preview, isLoading, error, uploadFile, previewFile, confirmImport, reset } = useImport()

const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const selectedAccountId = ref<number | undefined>(undefined)
const isDragging = ref(false)
const checkedRows = ref<PreviewRow[]>([])
const selectedMemberByGroup = ref<Record<string, number | undefined>>({})

const isPdfSelected = computed(() => isPdfFile(selectedFile.value))

interface RowGroup {
  cardholder: string | null
  rows: PreviewRow[]
}

const groupedRows = computed<RowGroup[]>(() => {
  if (!preview.value) return []
  const groups: RowGroup[] = []
  const indexByKey = new Map<string, number>()
  for (const row of preview.value.rows) {
    const cardholder = (row.metadata?.cardholder as string | undefined) ?? null
    const key = cardholder ?? '__none__'
    let idx = indexByKey.get(key)
    if (idx === undefined) {
      idx = groups.length
      indexByKey.set(key, idx)
      groups.push({ cardholder, rows: [] })
    }
    groups[idx].rows.push(row)
  }
  return groups
})

onMounted(() => {
  fetchAccounts()
  fetchMembers()
})

watch(preview, (value) => {
  checkedRows.value = value ? [...value.rows] : []
  selectedMemberByGroup.value = {}
  if (!value) return
  for (const row of value.rows) {
    const cardholder = row.metadata?.cardholder as string | undefined
    if (!cardholder) continue
    row.member_id = row.suggested_member_id ?? undefined
    if (!(cardholder in selectedMemberByGroup.value)) {
      selectedMemberByGroup.value[cardholder] = row.suggested_member_id ?? undefined
    }
  }
})

function onGroupMemberChange(cardholder: string, event: Event) {
  const value = (event.target as HTMLSelectElement).value
  const memberId = value ? Number(value) : undefined
  selectedMemberByGroup.value[cardholder] = memberId
  const group = groupedRows.value.find((g) => g.cardholder === cardholder)
  group?.rows.forEach((row) => { row.member_id = memberId })
}

function isPdfFile(file: File | null): boolean {
  if (!file) return false
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) selectedFile.value = input.files[0]
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file && (file.type === 'text/csv' || file.type === 'application/pdf' || file.name.endsWith('.csv') || file.name.endsWith('.pdf'))) {
    selectedFile.value = file
  }
}

async function handleUpload() {
  if (!selectedFile.value) return
  if (isPdfFile(selectedFile.value)) {
    await previewFile(selectedFile.value, selectedAccountId.value)
  } else {
    await uploadFile(selectedFile.value, selectedAccountId.value)
  }
}

async function handleConfirm() {
  if (!checkedRows.value.length) return
  await confirmImport(checkedRows.value, selectedAccountId.value)
}

function handleReset() {
  reset()
  selectedFile.value = null
  selectedAccountId.value = undefined
  checkedRows.value = []
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function goToTransactions() {
  router.push('/transacoes')
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function adapterLabel(adapter: string): string {
  const labels: Record<string, string> = {
    itau_extrato: 'Extrato Itaú (conta-corrente)',
    itau_fatura: 'Fatura Itaú (cartão de crédito)',
  }
  return labels[adapter] ?? adapter
}

function formatRowDate(iso: string): string {
  const [year, month, day] = iso.split('-')
  return `${day}/${month}/${year}`
}

function formatRowAmount(amount: string): string {
  const value = Number(amount)
  const formatted = Math.abs(value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return `${value < 0 ? '-' : '+'} R$ ${formatted}`
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--bd2);
  border-radius: 10px;
  padding: 32px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: border-color .15s, background .15s;
  color: var(--t3);
  margin-bottom: 16px;
}

.drop-zone:hover,
.drop-zone:focus-visible {
  border-color: var(--blue);
  background: color-mix(in srgb, var(--blue) 5%, transparent);
  outline: none;
}

.drop-zone.dragging {
  border-color: var(--blue);
  background: color-mix(in srgb, var(--blue) 8%, transparent);
}

.drop-zone.has-file {
  border-color: var(--ok);
  border-style: solid;
  background: color-mix(in srgb, var(--ok) 5%, transparent);
  color: var(--ok);
}

.fi {
  margin-bottom: 0;
}

.fi-sel {
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
  padding-right: 32px;
}

.sel-wrap {
  position: relative;
}

.sel-caret {
  position: absolute;
  right: 11px;
  top: 50%;
  transform: translateY(-60%);
  color: var(--t3);
  font-size: 12px;
  pointer-events: none;
  line-height: 1;
}

.result-card {
  border-radius: 10px;
  padding: 24px;
  text-align: center;
  margin-bottom: 4px;
}

.result-card.all-ok {
  background: color-mix(in srgb, var(--ok) 8%, var(--sf));
  border: 1px solid color-mix(in srgb, var(--ok) 30%, transparent);
}

.result-card.has-errors {
  background: color-mix(in srgb, var(--warn) 8%, var(--sf));
  border: 1px solid color-mix(in srgb, var(--warn) 30%, transparent);
}
</style>
