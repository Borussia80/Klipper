/**
 * CONN-2: a API roda no plano Free do Render e dorme depois de um tempo sem
 * uso. A primeira requisição depois disso leva dezenas de segundos, e a tela
 * hoje fica parada sem dizer nada — indistinguível de travamento.
 *
 * O aviso só aparece depois de 1 segundo: requisição rápida não pode piscar
 * mensagem de servidor dormindo na cara do usuário.
 */
import { defineComponent, nextTick } from 'vue'
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import { useServerWaking } from '../useServerWaking'

/** Promessa que só resolve quando o teste mandar. */
function deferred<T>() {
  let settle!: (value: T) => void
  let fail!: (reason: unknown) => void
  const promise = new Promise<T>((resolve, reject) => {
    settle = resolve
    fail = reject
  })
  return { promise, settle, fail }
}

async function mountHarness() {
  let api!: ReturnType<typeof useServerWaking>
  const Harness = defineComponent({
    setup() {
      api = useServerWaking()
      return () => null
    },
  })
  await mountSuspended(Harness)
  return api
}

describe('useServerWaking', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('não avisa quando a resposta chega antes de 1 segundo', async () => {
    const { isWaking, track } = await mountHarness()
    const lenta = deferred<string>()

    const chamada = track(() => lenta.promise)
    await vi.advanceTimersByTimeAsync(900)

    expect(isWaking.value).toBe(false)

    lenta.settle('ok')
    await chamada
  })

  it('avisa quando a requisição passa de 1 segundo sem resposta', async () => {
    const { isWaking, track } = await mountHarness()
    const lenta = deferred<string>()

    const chamada = track(() => lenta.promise)
    await vi.advanceTimersByTimeAsync(1_000)
    await nextTick()

    expect(isWaking.value).toBe(true)

    lenta.settle('ok')
    await chamada
  })

  it('tira o aviso quando a resposta finalmente chega', async () => {
    const { isWaking, track } = await mountHarness()
    const lenta = deferred<string>()

    const chamada = track(() => lenta.promise)
    await vi.advanceTimersByTimeAsync(1_000)
    lenta.settle('ok')
    await chamada
    await nextTick()

    expect(isWaking.value).toBe(false)
  })

  // Sem o `finally`, uma requisição que falha deixa o aviso preso na tela para
  // sempre — o usuário vê "acordando" num servidor que já respondeu erro.
  it('tira o aviso mesmo quando a requisição falha', async () => {
    const { isWaking, track } = await mountHarness()
    const lenta = deferred<string>()

    const chamada = track(() => lenta.promise)
    await vi.advanceTimersByTimeAsync(1_000)
    lenta.fail(new Error('502'))

    await expect(chamada).rejects.toThrow('502')
    await nextTick()
    expect(isWaking.value).toBe(false)
  })

  // O dashboard dispara várias chamadas juntas. Se a contagem fosse booleana,
  // a primeira a terminar apagaria o aviso com as outras ainda esperando.
  it('mantém o aviso enquanto outra requisição lenta continua em voo', async () => {
    const { isWaking, track } = await mountHarness()
    const primeira = deferred<string>()
    const segunda = deferred<string>()

    const a = track(() => primeira.promise)
    const b = track(() => segunda.promise)
    await vi.advanceTimersByTimeAsync(1_000)
    await nextTick()
    expect(isWaking.value).toBe(true)

    primeira.settle('ok')
    await a
    await nextTick()
    expect(isWaking.value).toBe(true)

    segunda.settle('ok')
    await b
    await nextTick()
    expect(isWaking.value).toBe(false)
  })
})
