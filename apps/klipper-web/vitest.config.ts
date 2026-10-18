import { defineVitestConfig } from '@nuxt/test-utils/config'

// O runner do CI é UTC, e em UTC os testes de fuso passam mesmo com o bug:
// `new Date('2026-01-01')` só volta um dia onde o offset é negativo. Rodar a
// suíte no fuso do usuário é o que faz o guard de data ter efeito no CI, e não
// só na máquina de quem escreveu o teste.
process.env.TZ = 'America/Sao_Paulo'

// O default do `nuxt.config.ts` é `http://localhost:3000`, que é justamente
// onde o Rails fica quando se roda a API local. Aí todo `mountSuspended` passa
// pelo `auth.global.ts`, dispara o refresh de verdade e o socket conecta — e
// num teste com `vi.useFakeTimers()` nem o retry do ofetch nem o I/O do undici
// chegam a rodar, então o `Suspense` nunca resolve e o mount pendura até
// estourar. O CI não vê isso porque lá ninguém escuta a 3000. Apontar para uma
// porta morta é o que mantém a suíte fora da rede; quem quiser rodar contra uma
// API de verdade ainda pode exportar a variável.
process.env.NUXT_PUBLIC_API_URL ||= 'http://127.0.0.1:9'

export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    environmentOptions: {
      nuxt: {
        domEnvironment: 'happy-dom',
      },
    },
  },
})
