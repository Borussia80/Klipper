<template>
  <div
    role="main"
    aria-label="Autenticação Klipper"
    style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);padding:24px"
  >
    <div style="width:min(400px, 100% - 48px);text-align:center">

      <!-- Brand -->
      <img
        src="/klipper-mark.png"
        alt="Klipper"
        style="width:40px;height:40px;border-radius:10px;margin:0 auto 14px;display:block"
      >
      <div style="font-size:28px;font-weight:300;letter-spacing:-.03em;color:var(--t1);line-height:1.15">Klipper</div>
      <div style="font-size:13px;color:var(--t3);margin-top:4px;margin-bottom:48px;letter-spacing:.02em;text-transform:uppercase;font-family:'Space Grotesk',monospace;font-size:11px">Wealth OS</div>

      <!-- Error message -->
      <div
        v-if="error"
        style="background:rgba(232,53,53,0.1);border:1px solid rgba(232,53,53,0.25);border-radius:var(--r);padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px;text-align:left"
        role="alert"
      >
        {{ error }}
      </div>

      <!-- Email/password -->
      <div style="margin-top:16px">
        <div style="text-align:left">
          <div v-if="mode === 'signup'" style="margin-bottom:10px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'Space Grotesk',monospace;text-transform:uppercase;letter-spacing:.06em">Nome</label>
            <input
              v-model="nameField"
              type="text"
              autocomplete="name"
              placeholder="Seu nome"
              aria-label="Nome"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
            />
          </div>
          <div style="margin-bottom:10px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'Space Grotesk',monospace;text-transform:uppercase;letter-spacing:.06em">E-mail</label>
            <input
              v-model="emailField"
              type="email"
              autocomplete="email"
              placeholder="voce@email.com"
              aria-label="E-mail"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
              @keydown.enter="handleSubmit"
            />
          </div>
          <div :style="{ marginBottom: mode === 'signup' ? '10px' : '14px' }">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'Space Grotesk',monospace;text-transform:uppercase;letter-spacing:.06em">Senha</label>
            <input
              v-model="passwordField"
              type="password"
              :autocomplete="mode === 'signup' ? 'new-password' : 'current-password'"
              placeholder="••••••••"
              aria-label="Senha"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
              @keydown.enter="handleSubmit"
            />
          </div>
          <div v-if="mode === 'signup'" style="margin-bottom:14px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'Space Grotesk',monospace;text-transform:uppercase;letter-spacing:.06em">Confirmar senha</label>
            <input
              v-model="passwordConfirmationField"
              type="password"
              autocomplete="new-password"
              placeholder="••••••••"
              aria-label="Confirmar senha"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
              @keydown.enter="handleSubmit"
            />
          </div>
          <button
            class="btn btn-p"
            style="width:100%;height:40px;font-size:13px"
            :disabled="isLoading"
            type="button"
            @click="handleSubmit"
          >
            <span v-if="isLoading" class="btn-spinner" />
            <span v-else>{{ mode === 'signup' ? 'Criar conta' : 'Entrar' }}</span>
          </button>
        </div>
      </div>

      <!-- Footer link -->
      <div style="margin-top:28px;font-size:12px;color:var(--t4)">
        <template v-if="mode === 'login'">
          Não tem conta?
          <button type="button" style="background:none;border:none;padding:0;color:var(--blt);text-decoration:none;margin-left:4px;cursor:pointer;font-size:inherit" @click="switchMode('signup')">Criar conta</button>
        </template>
        <template v-else>
          Já tem conta?
          <button type="button" style="background:none;border:none;padding:0;color:var(--blt);text-decoration:none;margin-left:4px;cursor:pointer;font-size:inherit" @click="switchMode('login')">Entrar</button>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const isLoading = ref(false)
const error = ref<string | null>(null)

// Email + password login / signup
const { login, signUp } = useAuth()
const mode = ref<'login' | 'signup'>('login')
const nameField = ref('')
const emailField = ref('')
const passwordField = ref('')
const passwordConfirmationField = ref('')

function switchMode(next: 'login' | 'signup') {
  mode.value = next
  error.value = null
}

async function handleSubmit() {
  if (mode.value === 'signup') {
    await handleSignUp()
  } else {
    await handleEmailLogin()
  }
}

async function handleEmailLogin() {
  if (!emailField.value || !passwordField.value) return
  isLoading.value = true
  error.value = null
  try {
    await login(emailField.value, passwordField.value)
  } catch (e: unknown) {
    const msg = (e as { data?: { error?: string } })?.data?.error
    error.value = msg || 'E-mail ou senha incorretos.'
  } finally {
    isLoading.value = false
  }
}

async function handleSignUp() {
  if (!emailField.value || !passwordField.value) return
  if (passwordField.value !== passwordConfirmationField.value) {
    error.value = 'As senhas não conferem.'
    return
  }
  isLoading.value = true
  error.value = null
  try {
    await signUp(emailField.value, passwordField.value, nameField.value || undefined)
  } catch (e: unknown) {
    const msgs = (e as { data?: { errors?: string[]; error?: string } })?.data
    error.value = msgs?.errors?.join(', ') || msgs?.error || 'Não foi possível criar a conta.'
  } finally {
    isLoading.value = false
  }
}
</script>
