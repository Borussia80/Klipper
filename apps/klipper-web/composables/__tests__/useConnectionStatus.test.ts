import { defineComponent, nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import { useConnectionStatus } from '../useConnectionStatus'

describe('useConnectionStatus', () => {
  it('reflete navigator.onLine e reage aos eventos do navegador', async () => {
    Object.defineProperty(window.navigator, 'onLine', { configurable: true, value: false })
    const Harness = defineComponent({
      setup() {
        const { isOffline } = useConnectionStatus()
        return { isOffline }
      },
      template: '<output>{{ isOffline }}</output>',
    })

    const wrapper = await mountSuspended(Harness)
    expect(wrapper.text()).toBe('true')

    window.dispatchEvent(new Event('online'))
    await nextTick()
    expect(wrapper.text()).toBe('false')
  })
})
