import { describe, expect, it } from 'vitest'
import { resolveApiRouting } from '../apiRouting'

describe('resolveApiRouting', () => {
  it('sem proxy, aponta para a API local por padrão e não cria regras', () => {
    expect(resolveApiRouting({})).toEqual({ apiBase: 'http://localhost:3001', routeRules: {} })
  })

  it('sem proxy, respeita NUXT_PUBLIC_API_URL explícito', () => {
    const routing = resolveApiRouting({ NUXT_PUBLIC_API_URL: 'https://api.exemplo.com' })
    expect(routing.apiBase).toBe('https://api.exemplo.com')
    expect(routing.routeRules).toEqual({})
  })

  it('com proxy, chama a API na mesma origem e encaminha /api/** ao destino', () => {
    const routing = resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'https://klipper-api.onrender.com' })
    expect(routing.apiBase).toBe('')
    expect(routing.routeRules).toEqual({
      '/api/**': { proxy: 'https://klipper-api.onrender.com/api/**' },
    })
  })

  it('com proxy, ignora barra final no destino', () => {
    const routing = resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'https://klipper-api.onrender.com/' })
    expect(routing.routeRules['/api/**']).toEqual({ proxy: 'https://klipper-api.onrender.com/api/**' })
  })

  it('com proxy, mesma origem prevalece sobre NUXT_PUBLIC_API_URL cross-site', () => {
    const routing = resolveApiRouting({
      KLIPPER_API_PROXY_TARGET: 'https://klipper-api.onrender.com',
      NUXT_PUBLIC_API_URL: 'https://klipper-api.onrender.com',
    })
    expect(routing.apiBase).toBe('')
  })

  it('na Vercel, usa o NUXT_PUBLIC_API_URL https do build como destino do proxy', () => {
    const routing = resolveApiRouting({ VERCEL: '1', NUXT_PUBLIC_API_URL: 'https://klipper-api.onrender.com' })
    expect(routing.apiBase).toBe('')
    expect(routing.routeRules).toEqual({
      '/api/**': { proxy: 'https://klipper-api.onrender.com/api/**' },
    })
  })

  it('na Vercel, KLIPPER_API_PROXY_TARGET prevalece sobre NUXT_PUBLIC_API_URL', () => {
    const routing = resolveApiRouting({
      VERCEL: '1',
      KLIPPER_API_PROXY_TARGET: 'https://api.nova.com',
      NUXT_PUBLIC_API_URL: 'https://klipper-api.onrender.com',
    })
    expect(routing.routeRules['/api/**']).toEqual({ proxy: 'https://api.nova.com/api/**' })
  })

  it('na Vercel sem URL da API, mantém o padrão local sem proxy', () => {
    expect(resolveApiRouting({ VERCEL: '1' })).toEqual({ apiBase: 'http://localhost:3001', routeRules: {} })
  })

  it('rejeita destino de proxy que não seja https', () => {
    expect(() => resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'http://klipper-api.onrender.com' })).toThrow(/https/)
  })

  it('aceita http só para a API local', () => {
    const routing = resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'http://localhost:3001' })
    expect(routing.routeRules['/api/**']).toEqual({ proxy: 'http://localhost:3001/api/**' })
  })
})
