type ToastVariant = 'ok' | 'alert' | 'warn'

interface Toast {
  id: string
  message: string
  variant: ToastVariant
}

const toasts = ref<Toast[]>([])

export function useToast() {
  function addToast(message: string, variant: ToastVariant = 'ok', duration = 3000) {
    const id = Math.random().toString(36).slice(2)
    toasts.value.push({ id, message, variant })
    setTimeout(() => removeToast(id), duration)
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts: readonly(toasts), addToast, removeToast }
}
