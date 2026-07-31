export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  ssr: true,

  runtimeConfig: {
    apiUrlInternal: '',
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:3000',
      cookieSecure: '',
    },
  },

  modules: [
    '@nuxt/image',
    '@nuxt/fonts',
    '@nuxt/eslint',
    '@vite-pwa/nuxt',
  ],

  fonts: {
    families: [
      { name: 'Inter', provider: 'google', weights: [400, 500, 600] },
      { name: 'Space Grotesk', provider: 'google', weights: [400, 500, 600, 700] },
    ],
    defaults: {
      preload: true,
    },
  },

  css: ['~/assets/css/tokens.css', '~/assets/css/main.css'],

  app: {
    head: {
      htmlAttrs: { lang: 'pt-BR' },
      title: 'Klipper — Wealth OS',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Seu patrimônio, com clareza. Klipper é um sistema operacional financeiro pessoal: orçamento, investimentos e fluxo de caixa em um só lugar.',
        },
        { name: 'theme-color', content: '#0C1220' },
        { property: 'og:title', content: 'Klipper — Wealth OS' },
        { property: 'og:type', content: 'website' },
      ],
    },
  },

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Klipper — Wealth OS',
      short_name: 'Klipper',
      description: 'Seu sistema operacional financeiro pessoal',
      theme_color: '#07121E',
      background_color: '#07121E',
      display: 'standalone',
      orientation: 'portrait',
      icons: [
        { src: '/klipper-mark.png', sizes: '192x192', type: 'image/png' },
        { src: '/klipper-mark.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
      // SEC-16: /api/v1/* nunca é cacheado pelo Service Worker — são respostas
      // financeiras (saldos, transações, investimentos) e não devem persistir
      // em disco via Cache Storage. Sem regra de runtimeCaching, o workbox não
      // intercepta essas requisições; elas seguem direto pra rede.
      runtimeCaching: [],
    },
  },

})
