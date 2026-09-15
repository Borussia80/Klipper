<script setup lang="ts">
const { isWaking } = useServerWaking()
</script>

<template>
  <Transition name="waking">
    <div v-if="isWaking" class="waking-notice" role="status" aria-live="polite">
      <span class="waking-spinner" aria-hidden="true" />
      <span>Servidor acordando. Isso pode levar alguns segundos.</span>
    </div>
  </Transition>
</template>

<style scoped>
.waking-notice {
  position: fixed;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 300;
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: calc(100vw - 32px);
  padding: 8px 14px;
  border: 1px solid var(--bd);
  border-radius: 999px;
  background: var(--bg-frame);
  box-shadow: 0 4px 16px rgb(0 0 0 / 12%);
  font-size: 13px;
  color: var(--t2);
}

.waking-spinner {
  flex-shrink: 0;
  width: 12px;
  height: 12px;
  border: 2px solid var(--bd);
  border-top-color: var(--brass);
  border-radius: 50%;
  animation: waking-spin 0.7s linear infinite;
}

@keyframes waking-spin {
  to { transform: rotate(360deg); }
}

.waking-enter-active,
.waking-leave-active {
  transition: opacity 0.2s ease;
}

.waking-enter-from,
.waking-leave-to {
  opacity: 0;
}

/* Animação é sinal de "ainda estamos esperando", não enfeite: sem ela o aviso
   ainda precisa aparecer e sumir. */
@media (prefers-reduced-motion: reduce) {
  .waking-spinner {
    animation: none;
  }

  .waking-enter-active,
  .waking-leave-active {
    transition: none;
  }
}
</style>
