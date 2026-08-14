<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()

const isNotFound = computed(() => props.error.statusCode === 404)

const title = computed(() => (isNotFound.value ? 'Página não encontrada' : 'Algo deu errado'))
const description = computed(() =>
  isNotFound.value
    ? 'O endereço acessado não existe ou foi movido.'
    : 'Ocorreu um erro inesperado. Tente novamente em alguns instantes.'
)

function goHome() {
  clearError({ redirect: '/dashboard' })
}
</script>

<template>
  <div class="error-page">
    <div class="error-card">
      <span class="error-code mono">{{ error.statusCode }}</span>
      <h1 class="error-title">{{ title }}</h1>
      <p class="error-desc">{{ description }}</p>
      <button class="btn btn-p" type="button" @click="goHome">Voltar ao início</button>
    </div>
  </div>
</template>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  padding: 24px;
}

.error-card {
  max-width: 360px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.error-code {
  font-size: 13px;
  color: var(--alert);
  letter-spacing: 0.04em;
}

.error-title {
  font-size: 20px;
  color: var(--t1);
  margin: 4px 0 0;
}

.error-desc {
  font-size: 13px;
  color: var(--t3);
  margin: 0 0 12px;
}
</style>
