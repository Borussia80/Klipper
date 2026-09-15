import { ref } from 'vue'
import { describe, expect, it, beforeEach } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import ServerWakingNotice from '../ServerWakingNotice.vue'

const isWaking = ref(false)
mockNuxtImport('useServerWaking', () => () => ({ isWaking, track: <T>(c: () => Promise<T>) => c() }))

describe('ServerWakingNotice.vue', () => {
  beforeEach(() => {
    isWaking.value = false
  })

  it('não mostra nada enquanto o servidor responde no tempo normal', async () => {
    const wrapper = await mountSuspended(ServerWakingNotice)

    expect(wrapper.text()).toBe('')
  })

  it('anuncia que o servidor está acordando quando a espera se estende', async () => {
    isWaking.value = true
    const wrapper = await mountSuspended(ServerWakingNotice)

    expect(wrapper.text()).toContain('acordando')
  })

  // Sem `role="status"`, quem usa leitor de tela continua diante de uma tela
  // parada e silenciosa — que é exatamente o problema que este aviso resolve.
  it('anuncia por região viva, para leitor de tela', async () => {
    isWaking.value = true
    const wrapper = await mountSuspended(ServerWakingNotice)

    expect(wrapper.find('[role="status"]').attributes('aria-live')).toBe('polite')
  })
})
