<script setup lang="ts">
import { GLOBAL_SHORTCUTS } from '~/composables/useKeyboardShortcuts'

const { open, activeModal } = useModal()
const router = useRouter()

onMounted(() => {
  function handleKeyboard(e: KeyboardEvent) {
    const tag = (document.activeElement as HTMLElement)?.tagName
    const isEditable =
      tag === 'INPUT' ||
      tag === 'TEXTAREA' ||
      tag === 'SELECT' ||
      (document.activeElement as HTMLElement)?.isContentEditable

    // Não interrompe um modal já aberto — trocá-lo por outro (ex: a command
    // palette) descartaria o que a pessoa estava preenchendo nele.
    if (activeModal.value !== null) return

    // Cmd+K/Ctrl+K abre a command palette mesmo com um input comum focado
    // (busca global, como em outros apps) — só não com um modal aberto.
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault()
      open('command-palette')
      return
    }

    if (isEditable) return

    // Atalhos de letra única (quando fora de inputs, sem modificador)
    if (e.metaKey || e.ctrlKey || e.altKey) return

    const key = e.key.toLowerCase()
    if (key === '/' || key === 'k') {
      e.preventDefault()
      open('command-palette')
      return
    }

    const shortcut = Object.values(GLOBAL_SHORTCUTS).find((s) => s.key === key)
    if (!shortcut) return

    e.preventDefault()
    if (shortcut.actionType === 'modal') {
      open(shortcut.target)
    } else {
      router.push(shortcut.target)
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
    <LayoutMobileNav />
    <UiModalMount />
    <UiToastStack />
  </div>
</template>
