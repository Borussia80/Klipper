export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  ssr: true,

  modules: [
    '@nuxt/image',
    '@nuxt/fonts',
  ],

  fonts: {
    families: [
      { name: 'Space Grotesk', provider: 'google', weights: [400, 500, 600, 700] },
      { name: 'Inter', provider: 'google', weights: [400, 500] },
      { name: 'Geist Mono', provider: 'google', weights: [400, 500] },
    ],
    defaults: {
      preload: true,
    },
  },

  css: ['~/assets/css/tokens.css', '~/assets/css/main.css'],

  app: {
    head: {
      htmlAttrs: { lang: 'pt-BR' },
      title: 'Quebec — Software independente',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Ferramentas de precisão para a vida real. Construímos software que transforma sistemas complexos em experiências simples, rápidas e duráveis.',
        },
        { name: 'theme-color', content: '#060A12' },
        { property: 'og:title', content: 'Quebec — Software independente' },
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: 'https://quebec.com.br' },
      ],
    },
  },
})
