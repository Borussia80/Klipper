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
      <div style="font-size:13px;color:var(--t3);margin-top:4px;margin-bottom:48px;letter-spacing:.02em;text-transform:uppercase;font-family:'JetBrains Mono',monospace;font-size:11px">Wealth OS</div>

      <!-- Key ring focal element -->
      <div
        class="key-ring"
        aria-hidden="true"
        style="width:80px;height:80px;border:2px solid var(--blue);border-radius:50%;box-shadow:0 0 24px rgba(43,125,244,0.25);display:flex;align-items:center;justify-content:center;margin:0 auto 20px;color:var(--blt)"
      >
        <KeyRound :size="32" :stroke-width="1.5" />
      </div>
      <div style="font-size:13px;color:var(--t3);margin-bottom:28px">Toque para entrar com Passkey</div>

      <!-- Error message -->
      <div
        v-if="error"
        style="background:rgba(232,53,53,0.1);border:1px solid rgba(232,53,53,0.25);border-radius:var(--r);padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px;text-align:left"
        role="alert"
      >
        {{ error }}
      </div>

      <!-- Passkey CTA -->
      <button
        class="btn btn-p"
        style="width:100%;height:44px;font-size:13px;margin-bottom:16px"
        :disabled="isLoading"
        aria-label="Entrar com Passkey biométrico"
        @click="attemptPasskeyLogin"
      >
        <span v-if="isLoading" class="btn-spinner" />
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
          <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
        </svg>
        {{ isLoading ? 'Autenticando…' : 'Entrar com Passkey' }}
      </button>

      <!-- Divider -->
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
        <div style="flex:1;height:1px;background:var(--bd2)"></div>
        <span style="font-size:11px;color:var(--t4)">ou</span>
        <div style="flex:1;height:1px;background:var(--bd2)"></div>
      </div>

      <!-- Google -->
      <button
        class="btn"
        style="width:100%;height:44px;font-size:13px;background:transparent;border:1px solid var(--bd2);color:var(--t2);margin-bottom:10px"
        aria-label="Continuar com Google"
      >
        <!-- Google "G" SVG -->
        <svg width="16" height="16" viewBox="0 0 24 24" style="flex-shrink:0">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Continuar com Google
      </button>

      <!-- Apple -->
      <button
        class="btn"
        style="width:100%;height:44px;font-size:13px;background:transparent;border:1px solid var(--bd2);color:var(--t2)"
        aria-label="Continuar com Apple"
      >
        <!-- Apple logo approximation -->
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="flex-shrink:0">
          <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
        </svg>
        Continuar com Apple
      </button>

      <!-- Email/password fallback -->
      <div style="margin-top:16px">
        <button
          style="background:none;border:none;font-size:12px;color:var(--t4);cursor:pointer;padding:0;text-decoration:underline"
          type="button"
          @click="showEmailForm = !showEmailForm"
        >
          {{ showEmailForm ? 'Ocultar' : 'Entrar com e-mail e senha' }}
        </button>

        <div v-if="showEmailForm" style="margin-top:14px;text-align:left">
          <div style="margin-bottom:10px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.06em">E-mail</label>
            <input
              v-model="emailField"
              type="email"
              autocomplete="email"
              placeholder="voce@email.com"
              aria-label="E-mail"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
              @keydown.enter="handleEmailLogin"
            />
          </div>
          <div style="margin-bottom:14px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.06em">Senha</label>
            <input
              v-model="passwordField"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              aria-label="Senha"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
              @keydown.enter="handleEmailLogin"
            />
          </div>
          <button
            class="btn btn-p"
            style="width:100%;height:40px;font-size:13px"
            :disabled="isLoading"
            type="button"
            @click="handleEmailLogin"
          >
            <span v-if="isLoading" class="btn-spinner" />
            <span v-else>Entrar</span>
          </button>
        </div>
      </div>

      <!-- Footer link -->
      <div style="margin-top:28px;font-size:12px;color:var(--t4)">
        Não tem conta?
        <NuxtLink to="/onboarding" style="color:var(--blt);text-decoration:none;margin-left:4px">Criar conta</NuxtLink>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { KeyRound } from 'lucide-vue-next'

definePageMeta({ layout: false })

const isLoading = ref(false)
const error = ref<string | null>(null)

async function attemptPasskeyLogin() {
  isLoading.value = true
  error.value = null
  try {
    // WebAuthn credential assertion — requires backend integration
    // const credential = await navigator.credentials.get({ publicKey: { ... } })
    // For now, navigate to onboarding
    await navigateTo('/onboarding')
  } catch {
    error.value = 'Não foi possível autenticar. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}

// Email + password login
const { login } = useAuth()
const showEmailForm = ref(false)
const emailField = ref('')
const passwordField = ref('')

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
</script>

<style scoped>
@media (prefers-reduced-motion: no-preference) {
  .key-ring {
    animation: ring-pulse 2.5s ease-in-out infinite;
  }

  @keyframes ring-pulse {
    0%, 100% { box-shadow: 0 0 24px rgba(43, 125, 244, 0.25); }
    50%       { box-shadow: 0 0 48px rgba(43, 125, 244, 0.5); }
  }
}
</style>
