<script setup lang="ts">
const props = defineProps<{
  title: string
  subtitle?: string
  open: boolean
}>()

const emit = defineEmits<{ close: [] }>()

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

// Focus trap
const drawerRef = ref<HTMLElement | null>(null)
const { activate, deactivate } = useFocusTrap(drawerRef)
const triggerEl = ref<HTMLElement | null>(null)

watch(
  () => props.open,
  (open) => {
    if (open) {
      document.addEventListener('keydown', onKeydown)
      triggerEl.value = document.activeElement as HTMLElement
      nextTick(() => activate())
    } else {
      document.removeEventListener('keydown', onKeydown)
      deactivate(triggerEl.value)
    }
  },
)

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="open"
        ref="drawerRef"
        class="drawer"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        aria-labelledby="modal-title-id"
      >
        <!-- Accent stripe -->
        <div class="drawer-stripe"></div>

        <!-- Header -->
        <div class="drawer-header">
          <div>
            <div id="modal-title-id" class="drawer-title">{{ title }}</div>
            <div v-if="subtitle" class="drawer-subtitle">{{ subtitle }}</div>
          </div>
          <button class="btn btn-i drawer-close" aria-label="Fechar painel" @click="emit('close')">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <!-- Scrollable body -->
        <div class="drawer-body">
          <slot />
        </div>
      </div>
    </Transition>

    <!-- Backdrop -->
    <Transition name="fade">
      <div v-if="open" class="drawer-backdrop" aria-hidden="true" @click="emit('close')"></div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer {
  position: fixed;
  right: 0;
  top: 48px;
  bottom: 0;
  width: 420px;
  z-index: 200;
  background: var(--bg-frame);
  border-left: 1px solid var(--bd2);
  display: flex;
  flex-direction: column;
}

.drawer-stripe {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--blue), var(--blt), transparent);
  opacity: 0.4;
  pointer-events: none;
}

.drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px;
  flex-shrink: 0;
}

.drawer-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--t1);
  letter-spacing: -0.015em;
}

.drawer-subtitle {
  font-size: 11px;
  color: var(--t3);
  margin-top: 2px;
}

.drawer-close {
  flex-shrink: 0;
  margin-top: -2px;
}

.drawer-body {
  overflow-y: auto;
  padding: 0 20px 32px;
  flex: 1;
}

.drawer-backdrop {
  position: fixed;
  inset: 48px 0 0 0;
  z-index: 199;
  background: rgba(5, 12, 22, 0.72);
  backdrop-filter: blur(2px);
}

/* Drawer slide transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: transform 220ms ease-out;
}
.drawer-enter-from,
.drawer-leave-to {
  transform: translateX(100%);
}

/* Backdrop fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease-out;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile: fullscreen drawer */
@media (max-width: 640px) {
  .drawer {
    width: 100%;
    left: 0;
    top: 0;
    border-left: none;
    border-top: none;
  }
  .drawer-backdrop {
    inset: 0;
  }
}
</style>
