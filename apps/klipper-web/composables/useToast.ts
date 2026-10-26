type ToastVariant = 'ok' | 'alert' | 'warn'
export interface ToastAction {
  label: string
  // eslint-disable-next-line @typescript-eslint/no-invalid-void-type
  onClick: () => void | Promise<unknown>
}

interface Toast {
  id: string
  message: string
  variant: ToastVariant
  action?: ToastAction
}

const toasts = ref<Toast[]>([])

export function useToast() {
  function addToast(message: string, variant: ToastVariant = 'ok', duration = 3000, action?: ToastAction) {
    const id = Math.random().toString(36).slice(2)
    toasts.value.push({ id, message, variant, ...(action ? { action } : {}) })
    setTimeout(() => removeToast(id), duration)
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t: Toast) => t.id !== id)
  }

  return { toasts: readonly(toasts), addToast, removeToast }
}
