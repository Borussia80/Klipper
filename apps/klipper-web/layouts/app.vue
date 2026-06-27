<script setup lang="ts">
const { open } = useModal()

onMounted(() => {
  function handleKeyboard(e: KeyboardEvent) {
    const tag = (document.activeElement as HTMLElement)?.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      open('novo-lancamento')
    }
    if (e.key === 'n' && !e.metaKey && !e.ctrlKey && !e.altKey) {
      e.preventDefault()
      open('novo-lancamento')
    }
  }
  document.addEventListener('keydown', handleKeyboard)
  onUnmounted(() => document.removeEventListener('keydown', handleKeyboard))
})
</script>

<template>
  <div class="shell">
    <LayoutAppTopbar class="shell-header" />
    <LayoutAppSidebar class="shell-nav" />
    <main class="shell-main" style="overflow-y:auto;background:var(--bg);display:flex;flex-direction:column">
      <slot />
    </main>
    <LayoutRightPanel class="shell-panel" />
    <UiModalMount />
    <UiToastStack />
  </div>
</template>
