<template>
  <div
    role="main"
    aria-label="Esqueci minha senha"
    style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);padding:24px"
  >
    <div style="width:min(400px, 100% - 48px);text-align:center">

      <!-- Brand -->
      <img
        src="/klipper-mark.png"
        alt="Klipper"
        style="width:40px;height:40px;border-radius:10px;margin:0 auto 14px;display:block"
      >
      <div style="font-size:28px;font-weight:300;letter-spacing:-.03em;color:var(--t1);line-height:1.15">Recuperar senha</div>
      <div style="font-size:13px;color:var(--t3);margin-top:4px;margin-bottom:48px">Informe seu e-mail e enviaremos um link de redefinição.</div>

      <!-- Error message -->
      <div
        v-if="error"
        style="background:rgba(232,53,53,0.1);border:1px solid rgba(232,53,53,0.25);border-radius:var(--r);padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px;text-align:left"
        role="alert"
      >
        {{ error }}
      </div>

      <!-- Success message -->
      <div
        v-if="sent"
        style="background:rgba(53,232,120,0.1);border:1px solid rgba(53,232,120,0.25);border-radius:var(--r);padding:10px 14px;font-size:12px;color:var(--t1);margin-bottom:16px;text-align:left"
        role="status"
      >
        Se o e-mail existir, enviaremos um link de redefinição.
      </div>

      <div v-if="!sent" style="margin-top:16px">
        <div style="text-align:left">
          <div style="margin-bottom:14px">
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
          <button
            class="btn btn-p"
            style="width:100%;height:40px;font-size:13px"
            :disabled="isLoading"
            type="button"
            @click="handleSubmit"
          >
            <span v-if="isLoading" class="btn-spinner" />
            <span v-else>Enviar link</span>
          </button>
        </div>
      </div>

      <!-- Footer link -->
      <div style="margin-top:28px;font-size:12px;color:var(--t4)">
        <NuxtLink to="/login" style="color:var(--blt);text-decoration:none">Voltar para o login</NuxtLink>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const isLoading = ref(false)
const error = ref<string | null>(null)
const sent = ref(false)

const { requestPasswordReset } = useAuth()
const emailField = ref('')

async function handleSubmit() {
  if (!emailField.value) return
  isLoading.value = true
  error.value = null
  try {
    await requestPasswordReset(emailField.value)
    sent.value = true
  } catch {
    error.value = 'Não foi possível processar o pedido. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>
