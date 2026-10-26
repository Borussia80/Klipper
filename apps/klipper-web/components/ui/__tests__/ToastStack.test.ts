import { describe, it, expect, vi } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import { ref } from 'vue'

const mockRemoveToast = vi.fn()
const mockToasts = ref<Array<{
  id: string
  message: string
  variant: 'ok'
  action?: { label: string; onClick: () => undefined | Promise<unknown> }
}>>([])

mockNuxtImport('useToast', () => () => ({ toasts: mockToasts, removeToast: mockRemoveToast }))

describe('ToastStack', () => {
  it('runs the toast action and removes that toast', async () => {
    const onClick = vi.fn()
    mockToasts.value = [{ id: 'undo-1', message: 'Lançamento removido', variant: 'ok', action: { label: 'Desfazer', onClick } }]
    const { default: ToastStack } = await import('../ToastStack.vue')
    const wrapper = await mountSuspended(ToastStack)

    const actionButton = document.body.querySelector<HTMLButtonElement>('button.toast-action')
    expect(actionButton).not.toBeNull()
    actionButton!.click()
    await Promise.resolve()

    expect(onClick).toHaveBeenCalledOnce()
    expect(mockRemoveToast).toHaveBeenCalledWith('undo-1')
    wrapper.unmount()
    mockToasts.value = []
    mockRemoveToast.mockReset()
  })
})
