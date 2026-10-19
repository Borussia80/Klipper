<template>
  <div class="configuracoes">
    <div class="page-header">
      <div>
        <h2 class="page-h2">Configurações</h2>
        <p class="page-sub mono">Klipper v0.1.0</p>
      </div>
    </div>

    <div class="settings-grid">
      <div class="card settings-card">
        <p class="section-label">Conta</p>
        <div class="setting-row">
          <div>
            <p class="setting-name">{{ user?.name ?? 'Usuário' }}</p>
            <p class="setting-sub">{{ user?.email ?? '' }}</p>
          </div>
          <button class="btn btn-ghost btn-sm" @click="startEditing">Editar</button>
        </div>
        <form v-if="isEditing" style="display:flex;flex-direction:column;gap:10px" @submit.prevent="saveProfile">
          <input v-model="form.name" class="fi" aria-label="Nome" maxlength="80" placeholder="Nome">
          <input v-model="form.email" class="fi" aria-label="E-mail" type="email" placeholder="E-mail">
          <div>
            <p class="setting-name">Identidade para detectar transferências entre minhas contas</p>
            <p class="setting-sub">Serve só para SUGERIR transferências entre contas próprias.</p>
          </div>
          <div v-for="(_, index) in form.own_names" :key="index" style="display:flex;gap:8px">
            <input v-model="form.own_names[index]" class="fi" :aria-label="`Nome próprio ${index + 1}`" maxlength="80" placeholder="Nome usado nos extratos">
            <button class="btn btn-ghost btn-sm" type="button" aria-label="Remover nome" @click="form.own_names.splice(index, 1)">Remover</button>
          </div>
          <button v-if="form.own_names.length < 5" class="btn btn-ghost btn-sm" type="button" @click="form.own_names.push('')">Adicionar nome</button>
          <input v-model="form.own_cpf_mask" class="fi" aria-label="Seis dígitos centrais do CPF" maxlength="12" placeholder="123.456" @input="formatCpf">
          <p v-if="saveError" role="alert" class="setting-sub" style="color:var(--alert)">{{ saveError }}</p>
          <p v-if="saveSuccess" role="status" class="setting-sub" style="color:var(--ok)">Dados salvos.</p>
          <div style="display:flex;gap:8px">
            <button class="btn btn-p btn-sm" data-testid="save-profile" type="submit" :disabled="isSaving">{{ isSaving ? 'Salvando…' : 'Salvar' }}</button>
            <button class="btn btn-ghost btn-sm" type="button" @click="isEditing = false">Cancelar</button>
          </div>
        </form>
      </div>

      <div class="card settings-card">
        <p class="section-label">Aparência</p>
        <div class="setting-row">
          <p class="setting-name">Tema</p>
          <span class="badge badge--neutral">Escuro</span>
        </div>
        <div class="setting-row">
          <p class="setting-name">Moeda</p>
          <span class="badge badge--neutral mono">BRL</span>
        </div>
      </div>

      <div class="card settings-card">
        <p class="section-label">Sincronização</p>
        <div class="setting-row">
          <div>
            <p class="setting-name">API Klipper</p>
          </div>
          <span class="badge badge--positive">Online</span>
        </div>
      </div>

      <div class="card settings-card">
        <p class="section-label">Sessão</p>
        <div class="setting-row">
          <div>
            <p class="setting-name">Encerrar sessão</p>
            <p class="setting-sub">Sai da conta neste dispositivo</p>
          </div>
          <button class="btn btn-ghost btn-sm" @click="handleLogout">Sair</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', title: 'Configurações' })
const { user, logout, updateProfile } = useAuth()
const isEditing = ref(false)
const isSaving = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)
const form = reactive({ name: '', email: '', own_names: [] as string[], own_cpf_mask: '' })

function startEditing() {
  form.name = user.value?.name ?? ''
  form.email = user.value?.email ?? ''
  form.own_names = [...(user.value?.own_names ?? [])]
  form.own_cpf_mask = user.value?.own_cpf_mask ?? ''
  saveError.value = ''
  saveSuccess.value = false
  isEditing.value = true
}

function formatCpf() {
  const digits = form.own_cpf_mask.replace(/\D/g, '').slice(0, 6)
  form.own_cpf_mask = digits.length > 3 ? `${digits.slice(0, 3)}.${digits.slice(3)}` : digits
}

async function saveProfile() {
  isSaving.value = true
  saveError.value = ''
  saveSuccess.value = false
  try {
    await updateProfile({
      name: form.name,
      email: form.email,
      own_names: form.own_names.map((name: string) => name.trim()).filter(Boolean).slice(0, 5),
      own_cpf_mask: form.own_cpf_mask,
    })
    saveSuccess.value = true
  } catch {
    saveError.value = 'Não foi possível salvar. Tente novamente.'
  } finally {
    isSaving.value = false
  }
}

async function handleLogout() {
  await logout()
}
</script>

<style scoped>
.configuracoes {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 80px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.page-h2 {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--t1);
  margin-bottom: 4px;
}

.page-sub { font-size: 0.78rem; color: var(--t3); }

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 640px;
}

.settings-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--bd);
}

.setting-row:last-child { border-bottom: none; }

.setting-name {
  font-size: 0.875rem;
  color: var(--t1);
}

.setting-sub {
  font-size: 0.72rem;
  color: var(--t3);
  margin-top: 2px;
}
</style>
