export function useFocusTrap(containerRef: Ref<HTMLElement | null>) {
  const FOCUSABLE = [
    'a[href]', 'button:not([disabled])', 'input:not([disabled])',
    'select:not([disabled])', 'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ')

  function getFocusable(): HTMLElement[] {
    return containerRef.value
      ? [...containerRef.value.querySelectorAll<HTMLElement>(FOCUSABLE)]
      : []
  }

  function trap(e: KeyboardEvent) {
    if (e.key !== 'Tab') return
    const els = getFocusable()
    if (!els.length) return
    const first = els[0]
    const last = els[els.length - 1]
    if (e.shiftKey) {
      if (document.activeElement === first) { e.preventDefault(); last.focus() }
    } else {
      if (document.activeElement === last) { e.preventDefault(); first.focus() }
    }
  }

  function activate() {
    document.addEventListener('keydown', trap)
    const els = getFocusable()
    if (els.length) els[0].focus()
  }

  function deactivate(returnTo?: HTMLElement | null) {
    document.removeEventListener('keydown', trap)
    returnTo?.focus()
  }

  return { activate, deactivate }
}
