<template>
  <div
    role="main"
    aria-label="Redefinir senha"
    style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);padding:24px"
  >
    <div style="width:min(400px, 100% - 48px);text-align:center">

      <!-- Brand -->
      <img
        src="/klipper-mark.png"
        alt="Klipper"
        style="width:40px;height:40px;border-radius:10px;margin:0 auto 14px;display:block"
      >
      <div style="font-size:28px;font-weight:300;letter-spacing:-.03em;color:var(--t1);line-height:1.15">Nova senha</div>
      <div style="font-size:13px;color:var(--t3);margin-top:4px;margin-bottom:48px">Escolha uma nova senha para sua conta.</div>

      <!-- Error message -->
      <div
        v-if="error"
        style="background:rgba(232,53,53,0.1);border:1px solid rgba(232,53,53,0.25);border-radius:var(--r);padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px;text-align:left"
        role="alert"
      >
        {{ error }}
      </div>

      <div v-if="!token" style="font-size:13px;color:var(--t3)">
        Link inválido. <NuxtLink to="/esqueci-senha" style="color:var(--blt);text-decoration:none">Solicite um novo</NuxtLink>.
      </div>

      <div v-else style="margin-top:16px">
        <div style="text-align:left">
          <div style="margin-bottom:10px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'Space Grotesk',monospace;text-transform:uppercase;letter-spacing:.06em">Nova senha</label>
            <input
              v-model="passwordField"
              type="password"
              autocomplete="new-password"
              placeholder="••••••••"
              aria-label="Nova senha"
              style="width:100%;background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r);padding:9px 12px;color:var(--t1);font-size:13px;outline:none;box-sizing:border-box;font-family:inherit"
              @keydown.enter="handleSubmit"
            />
          </div>
          <div style="margin-bottom:14px">
            <label style="font-size:11px;color:var(--t3);display:block;margin-bottom:4px;font-family:'Space Grotesk',monospace;text-transform:uppercase;letter-spacing:.06em">Confirmar nova senha</label>
            <input
              v-model="passwordConfirmationField"
              type="password"
              autocomplete="new-password"
              placeholder="••••••••"
              aria-label="Confirmar nova senha"
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
            <span v-else>Redefinir senha</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const isLoading = ref(false)
const error = ref<string | null>(null)

const { confirmPasswordReset } = useAuth()
const route = useRoute()
const token = computed(() => (route.query.token as string) || '')

const passwordField = ref('')
const passwordConfirmationField = ref('')

async function handleSubmit() {
  if (!passwordField.value || !passwordConfirmationField.value) return
  if (passwordField.value !== passwordConfirmationField.value) {
    error.value = 'As senhas não conferem.'
    return
  }
  isLoading.value = true
  error.value = null
  try {
    await confirmPasswordReset(token.value, passwordField.value, passwordConfirmationField.value)
    await navigateTo('/login')
  } catch (e: unknown) {
    const msg = (e as { data?: { error?: string; errors?: string[] } })?.data
    error.value = msg?.error || msg?.errors?.join(', ') || 'Link inválido ou expirado.'
  } finally {
    isLoading.value = false
  }
}
</script>
