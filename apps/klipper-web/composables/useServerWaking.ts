/**
 * A API roda no plano Free do Render e dorme depois de um tempo sem uso. A
 * primeira requisição depois disso leva dezenas de segundos — tempo em que a
 * tela fica parada, indistinguível de travamento.
 */

/** Abaixo disso a espera é normal e avisar só assusta à toa. */
const WAKE_NOTICE_DELAY = 1_000

export function useServerWaking() {
  // Contagem, não booleano: o dashboard dispara várias chamadas juntas e a
  // primeira a terminar apagaria o aviso com as outras ainda esperando.
  const pending = useState<number>('klipper-server-waking', () => 0)

  async function track<T>(call: () => Promise<T>): Promise<T> {
    let counted = false
    const timer = setTimeout(() => {
      counted = true
      pending.value += 1
    }, WAKE_NOTICE_DELAY)

    try {
      return await call()
    } finally {
      clearTimeout(timer)
      if (counted) {
        pending.value -= 1
      }
    }
  }

  return {
    isWaking: computed(() => pending.value > 0),
    track,
  }
}
