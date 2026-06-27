<template>
  <Teleport to="body">
    <div class="toast-stack" aria-live="polite" aria-atomic="false">
      <TransitionGroup name="toast" tag="div">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="`toast-${toast.variant}`"
          role="status"
        >
          <span class="toast-dot" />
          <span class="toast-msg">{{ toast.message }}</span>
          <button class="toast-close btn-i" aria-label="Fechar" @click="removeToast(toast.id)">
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <path d="M1.5 1.5l7 7M8.5 1.5l-7 7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const { toasts, removeToast } = useToast()
</script>

<style scoped>
.toast-stack {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--sf);
  border: 1px solid var(--bd2);
  font-size: 13px;
  color: var(--t1);
  pointer-events: all;
  min-width: 240px;
  max-width: 340px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.toast-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.toast-ok   .toast-dot { background: var(--ok); }
.toast-alert .toast-dot { background: var(--alert); }
.toast-warn  .toast-dot { background: var(--warn); }

.toast-ok   { border-color: rgba(13,184,120,0.28); }
.toast-alert { border-color: rgba(232,53,53,0.28); }
.toast-warn  { border-color: rgba(229,144,16,0.28); }

.toast-msg { flex: 1; }

.toast-close {
  width: 22px; height: 22px;
  flex-shrink: 0;
}

/* Transitions */
.toast-enter-active { transition: all 200ms ease-out; }
.toast-leave-active { transition: all 160ms ease-in; }
.toast-enter-from   { opacity: 0; transform: translateY(12px) scale(0.96); }
.toast-leave-to     { opacity: 0; transform: translateX(16px); }

@media (max-width: 640px) {
  .toast-stack {
    bottom: 72px;
    right: 12px;
    left: 12px;
  }
  .toast { min-width: unset; max-width: unset; }
}
</style>
