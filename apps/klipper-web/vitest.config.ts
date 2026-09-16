import { defineVitestConfig } from '@nuxt/test-utils/config'

// O runner do CI é UTC, e em UTC os testes de fuso passam mesmo com o bug:
// `new Date('2026-01-01')` só volta um dia onde o offset é negativo. Rodar a
// suíte no fuso do usuário é o que faz o guard de data ter efeito no CI, e não
// só na máquina de quem escreveu o teste.
process.env.TZ = 'America/Sao_Paulo'

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
