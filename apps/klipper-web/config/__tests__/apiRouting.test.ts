import { describe, expect, it } from 'vitest'
import { resolveApiRouting } from '../apiRouting'

describe('resolveApiRouting', () => {
  it('sem proxy, aponta para a API local por padrão e não cria regras', () => {
    expect(resolveApiRouting({})).toEqual({ apiUrl: 'http://localhost:3001', routeRules: {} })
  })

  it('sem proxy, respeita NUXT_PUBLIC_API_URL explícito', () => {
    const routing = resolveApiRouting({ NUXT_PUBLIC_API_URL: 'https://api.exemplo.com' })
    expect(routing.apiUrl).toBe('https://api.exemplo.com')
    expect(routing.routeRules).toEqual({})
  })

  it('com proxy, chama a API na mesma origem e encaminha /api/** ao destino', () => {
    const routing = resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'https://klipper-api.onrender.com' })
    expect(routing.apiUrl).toBe('')
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
    expect(routing.apiUrl).toBe('')
  })

  it('rejeita destino de proxy que não seja https', () => {
    expect(() => resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'http://klipper-api.onrender.com' })).toThrow(/https/)
  })

  it('aceita http só para a API local', () => {
    const routing = resolveApiRouting({ KLIPPER_API_PROXY_TARGET: 'http://localhost:3001' })
    expect(routing.routeRules['/api/**']).toEqual({ proxy: 'http://localhost:3001/api/**' })
  })
})
